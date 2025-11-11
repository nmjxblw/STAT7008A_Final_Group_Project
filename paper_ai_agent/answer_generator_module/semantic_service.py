from typing import List, Dict, Any, Optional, AsyncGenerator
from collections import Counter
import asyncio
from openai import OpenAI
from .data_models import DemandType, Document, QueryResult, LLMConfig
from .deepseek_api import load_llm_config, build_deepseek_client
from .compute_relevance import relevance_calculator  # 导入独立的相关性计算器

def mock_documents() -> List[Document]:
    """模拟文档数据"""
    return [
        Document(
            file_id="75ac7d52",
            file_name="Attention Is All You Need.pdf",
            title="Attention Is All You Need: The Transformer Revolution in Sequence Modeling",
            summary=(
                "This paper introduces the Transformer, a neural network architecture based solely on attention, "
                "removing recurrence and convolution, enabling high parallelization and SOTA results on WMT14."
            ),
            keywords=[
                "transformer",
                "attention",
                "sequence",
                "machine translation",
                "parallelization",
            ],
            text_length=39448,
            file_type="pdf",
            extra_fields={"author": "Vaswani et al.", "year": "2017"},
        ),
        Document(
            file_id="9f3a21aa",
            file_name="Company Policy 2025.pdf",
            title="Company Policy and Approval Flow 2025",
            summary=(
                "This document describes internal approval flows, reimbursement rules, HR processes, and policy updates for 2025."
            ),
            keywords=["policy", "approval", "hr", "reimbursement"],
            text_length=6800,
            file_type="pdf",
            extra_fields={"department": "HR", "created_at": "2025-10-20"},
        ),
        Document(
            file_id="abcdef",
            file_name="Deep Reinforcement Curriculum",
            title="Deep Reinforcement Learning & Curriculum Learning",
            summary=(
                "This fake document introduces deep learning, reinforcement learning, curriculum learning."
            ),
            keywords=["deep learning", "reinforcement learning", "curriculum"],
            text_length=1000,
            file_type="pdf",
            extra_fields={},
        ),
    ]
'''
file_id, title, summary, content, keywords, author, publish_date, download_date, total_tokens, unique_tokens, text_length.




'''



class SemanticService:
    """
    语义服务层：
    1. 自动识别意图（文件查询/问答）
    2. 文档搜索与富集
    3. 基于上下文的LLM问答
    """

    def __init__(self, documents: Optional[List[Document]] = None):
        self._documents: List[Document] = documents or mock_documents()
        
        # 运行时状态
        self._current_demand_raw: str = ""
        self._current_demand_type: Optional[DemandType] = None
        self._current_query_results: List[QueryResult] = []
        self._stopped: bool = False
        
        # LLM配置与客户端
        self._llm_config: LLMConfig = load_llm_config()
        self._client: Optional[OpenAI] = build_deepseek_client(self._llm_config)

    # ======================
    # 公共API
    # ======================

    def set_demand(self, user_input: str) -> bool:
        """设置用户需求"""
        self._stopped = False
        self._current_demand_raw = user_input.strip()
        self._current_demand_type = self._classify_demand(user_input)
        self._current_query_results = self._search_and_enrich(user_input)
        return True

    def stop_current_task(self) -> bool:
        """停止当前任务（流式输出时使用）"""
        self._stopped = True
        return True

    def redo_task(self, user_input: str) -> bool:
        """重新运行任务"""
        return self.set_demand(user_input)

    def get_query_file(self) -> List[str]:
        """返回匹配的文档标题列表（用于UI）"""
        return [r.title for r in self._current_query_results]

    def get_qualified_files_info(self, top_n: int = 5) -> List[Dict[str, str]]:
        """返回Top N文档的结构化信息"""
        results: List[Dict[str, str]] = []
        for r in self._current_query_results[:top_n]:
            results.append({
                "doc_id": r.doc_id,
                "title": r.title,
                "relevance_percent": f"{r.relevance:.2f}%",
                "summary": r.summary,
                "key_fields_summary": r.key_fields_summary,
                "high_freq_terms": ", ".join([f"{k}:{v}" for k, v in r.high_freq_terms.items()]),
            })
        return results

    def get_query_task_result(self) -> List[Dict[str, str]]:
        """返回所有查询结果（调试用）"""
        return self.get_qualified_files_info(top_n=len(self._current_query_results))

    def get_LLM_reply(self) -> Any:
        """获取LLM回复"""
        if not self._current_demand_raw:
            return {"error": "no demand set"}

        # 文件查询：直接返回文档列表
        if self._current_demand_type == DemandType.FILE_QUERY:
            return {
                "type": "file_query",
                "query": self._current_demand_raw,
                "results": self.get_qualified_files_info(top_n=10),
            }
        
        # 问答：需要调用LLM
        if not self._client or not self._llm_config.api_key:
            return {"error": "QA without api key"}
        
        context_text = self._build_context_from_results(self._current_query_results)
        prompt = self._build_llm_prompt(query=self._current_demand_raw, context=context_text)

        try:
            resp = self._client.chat.completions.create(
                model=self._llm_config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self._llm_config.max_tokens,
                temperature=self._llm_config.temperature,
            )
            reply_text = resp.choices[0].message.content.strip()
        except Exception as e:
            reply_text = f"(LLM call failed) {e}"

        return {
            "type": "qa",
            "prompt_sent": prompt,
            "reply": reply_text,
        }

    async def stream_LLM_reply(self) -> AsyncGenerator[str, None]:
        """异步流式返回LLM回复"""
        reply_obj = self.get_LLM_reply()
        text = reply_obj.get("reply", "")
        for ch in text:
            if self._stopped:
                break
            yield ch
            await asyncio.sleep(0.01)

    def set_llm_config(
        self,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = None,
        base_url: Optional[str] = None,
    ) -> bool:
        """更新LLM配置并重建客户端"""
        if model is not None:
            self._llm_config.model = model
        if max_tokens is not None:
            self._llm_config.max_tokens = max_tokens
        if api_key is not None:
            self._llm_config.api_key = api_key
        if temperature is not None:
            self._llm_config.temperature = temperature
        if base_url is not None:
            self._llm_config.base_url = base_url

        self._client = build_deepseek_client(self._llm_config)
        return True

    # ======================
    # 内部方法：意图识别
    # ======================

    def _classify_demand(self, user_input: str) -> DemandType:
        """分类用户需求类型"""
        # 优先用LLM分类
        llm_label = self._classify_with_llm(user_input)
        if llm_label == "FILE":
            return DemandType.FILE_QUERY
        if llm_label == "QA":
            return DemandType.QA

        # 关键字 fallback
        text = user_input.lower()
        file_keywords = ["file", "document", "doc", "list", "show", "open", "report", "pdf", "find", "search"]
        qa_keywords = ["why", "how", "explain", "difference", "compare", "what is", "what's"]

        has_file = any(k in text for k in file_keywords)
        has_qa = any(k in text for k in qa_keywords)

        return DemandType.FILE_QUERY if has_file else DemandType.QA

    def _classify_with_llm(self, user_input: str) -> Optional[str]:
        """用LLM进行意图分类"""
        if not self._client:
            return None

        system_prompt = (
            "You are an intent classifier. "
            "You must answer with EXACTLY ONE WORD: 'FILE' or 'QA'. "
            "Do NOT explain.\n"
            "- If the user wants to search/list/view/find/open documents/files/reports -> answer FILE.\n"
            "- If the user asks for explanation/analysis/how-to/reasoning -> answer QA.\n"
            "- If it is mixed, prefer FILE."
        )
        user_prompt = f"User query:\n{user_input}\n\nYour answer (FILE or QA):"

        try:
            resp = self._client.chat.completions.create(
                model=self._llm_config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4,
                temperature=0.0,
            )
            raw = resp.choices[0].message.content.strip()
            raw = raw.replace(".", "").strip().upper()
            return raw if raw in ("FILE", "QA") else None
        except Exception:
            return None

    # ======================
    # 内部方法：搜索与富集（调用独立相关性计算器）
    # ======================

    def _search_and_enrich(self, query: str) -> List[QueryResult]:
        """基于关键词的搜索与结果富集"""
        # 调用独立模块的分词方法
        query_tokens = relevance_calculator.tokenize(query)
        results: List[QueryResult] = []

        # 计算文档相关性得分（调用独立模块）
        scored_docs = []
        for doc in self._documents:
            score = relevance_calculator.compute_relevance(query_tokens, doc)
            if score > 0:
                scored_docs.append((doc, score))

        if not scored_docs:
            return []

        # 归一化得分到0-100%
        max_score = max(s for _, s in scored_docs) or 1.0

        # 构建查询结果
        for doc, score in scored_docs:
            relevance_percent = (score / max_score) * 100.0
            results.append(
                QueryResult(
                    doc_id=doc.file_id,
                    title=doc.title,
                    relevance=relevance_percent,
                    summary=self._summarize_document(doc),
                    key_fields_summary=self._summarize_key_fields(doc),
                    high_freq_terms=self._extract_high_freq_terms(doc, query_tokens),
                )
            )

        # 按相关性排序
        results.sort(key=lambda x: x.relevance, reverse=True)
        return results

    # ======================
    # 内部方法：结果摘要
    # ======================

    def _summarize_document(self, doc: Document) -> str:
        """生成文档摘要"""
        if doc.file_type == "text":
            short_summary = doc.summary[:120]
            return short_summary + ("..." if len(doc.summary) > 120 else "")
        else:
            base = f"This file is of type '{doc.file_type}', with title '{doc.title}'."
            if doc.extra_fields:
                extra_str = ", ".join([f"{k}: {v}" for k, v in doc.extra_fields.items()])
                base += f" Extra fields: {extra_str}"
            return base

    def _summarize_key_fields(self, doc: Document) -> str:
        """生成文档关键字段摘要"""
        if not doc.extra_fields:
            return "No key fields."
        return "; ".join([f"{k}={v}" for k, v in doc.extra_fields.items()])

    def _extract_high_freq_terms(
        self, doc: Document, query_tokens: List[str], top_k: int = 5
    ) -> Dict[str, int]:
        """提取高频词汇"""
        all_tokens = (
            relevance_calculator.tokenize(doc.summary)  # 调用独立模块的分词方法
            + query_tokens
            + [t.lower() for t in doc.keywords]
        )
        return dict(Counter(all_tokens).most_common(top_k))

    # ======================
    # 内部方法：Prompt构建
    # ======================

    def _build_context_from_results(self, results: List[QueryResult]) -> str:
        """从查询结果构建LLM上下文"""
        blocks = []
        for r in results:
            blocks.append(f"[{r.doc_id}] {r.title}\n{r.summary}\n")
        return "\n".join(blocks)

    def _build_llm_prompt(self, *, query: str, context: str) -> str:
        """构建LLM提示词"""
        return f"""
You are an enterprise internal knowledge-base assistant. You can ONLY use the information in the following DOCUMENTS to answer the user's question. If the documents do not contain enough information, you MUST answer: "No valid reference."

[Answering rules]
1. Be concise and accurate.
2. If you cite a document, add its id in square brackets at the end of the sentence, e.g. [75ac7d52].
3. Do NOT invent information that is not in the documents.
4. If multiple documents mention the same thing, you can merge them and cite multiple ids, e.g. [75ac7d52][9f3a21aa].

[DOCUMENTS]
{context}

[USER QUESTION]
{query}

Start answering now:
""".strip()