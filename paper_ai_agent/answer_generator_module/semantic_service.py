from curses import meta
from tkinter.filedialog import Open
from typing import List, Dict, Any, Optional, AsyncGenerator
from collections import Counter
import asyncio
from openai import OpenAI
from openai.types.chat import ChatCompletion
from .data_models import DemandType, Document, QueryResult, LLMConfig
from .compute_relevance import relevance_calculator  # 导入独立的相关性计算器

from datetime import datetime
from global_module import answer_generator_config, API_KEY
from utility_module import SingletonMeta


def mock_documents() -> List[Document]:
    """Mock documents for testing the new database schema."""
    return [
        Document(
            file_id="doc_rag_qa_001",
            title="Designing a RAG-based Question Answering System",
            summary=(
                "An overview of Retrieval-Augmented Generation (RAG) architectures for LLM-based "
                "question answering, covering retrieval pipelines, vector databases, and response synthesis."
            ),
            content=(
                "This document describes a practical design for a RAG-based question answering system. "
                "We first discuss document ingestion and chunking strategies, then describe how to build "
                "a vector store using dense embeddings. The retrieval layer selects top-k relevant passages, "
                "which are then passed as context to a large language model. We also compare different "
                "prompting templates, discuss latency/throughput trade-offs, and outline evaluation "
                "metrics such as answer correctness, faithfulness, and grounding."
            ),
            keywords=[
                "rag",
                "llm",
                "question answering",
                "retrieval",
                "vector database",
                "system design",
            ],
            author="Alice Smith",
            publish_date=datetime(2024, 5, 12, 10, 30, 0),
            download_date=datetime(2024, 5, 13, 9, 15, 0),
            total_tokens=3200,
            unique_tokens=780,
            text_length=14500,
        ),
        Document(
            file_id="doc_arch_002",
            title="LLM Application Architecture for Enterprise Search",
            summary=(
                "A system design note for integrating large language models with enterprise search, "
                "including RAG, caching strategies, and access control."
            ),
            content=(
                "This internal design document explains how to combine an existing enterprise search "
                "stack with LLM-powered summarization and RAG-style question answering. We describe "
                "the API gateway, authentication and authorization layers, the search backend, and "
                "an LLM service that performs answer generation. The document also covers result "
                "reranking, safety filters, prompt logging, and observability dashboards."
            ),
            keywords=[
                "enterprise search",
                "llm",
                "rag",
                "system architecture",
                "observability",
            ],
            author="Bob Lee",
            publish_date=datetime(2024, 6, 3, 14, 0, 0),
            download_date=datetime(2024, 6, 3, 16, 45, 0),
            total_tokens=2700,
            unique_tokens=650,
            text_length=12000,
        ),
        Document(
            file_id="doc_policy_003",
            title="Company Policy and Approval Flow 2025",
            summary=(
                "Describes internal approval flows, reimbursement rules, HR processes, and policy updates "
                "for fiscal year 2025."
            ),
            content=(
                "This policy document defines the official approval flow for expenses, travel, procurement, "
                "and headcount requests. It also describes the reimbursement process, required documentation, "
                "standard processing times, and escalation paths. HR-related policy updates for 2025 include "
                "revisions to remote work guidelines, learning budgets, and performance review cycles."
            ),
            keywords=["policy", "approval", "hr", "reimbursement", "remote work"],
            author="HR Department",
            publish_date=datetime(2025, 1, 10, 9, 0, 0),
            download_date=datetime(2025, 1, 11, 11, 30, 0),
            total_tokens=1800,
            unique_tokens=420,
            text_length=8000,
        ),
        Document(
            file_id="doc_eval_004",
            title="Evaluation of RAG vs Vanilla LLM Question Answering",
            summary=(
                "An empirical comparison between vanilla LLM QA and RAG-based QA across multiple datasets, "
                "evaluating accuracy, hallucination rate, and latency."
            ),
            content=(
                "We benchmark a vanilla LLM question answering baseline against a RAG pipeline that augments "
                "the model with retrieved context. Using open-domain QA datasets, internal knowledge-base QA, "
                "and FAQ-style corpora, we measure exact match, F1, and human-rated faithfulness. Results "
                "show that RAG significantly reduces hallucinations while maintaining comparable latency when "
                "proper caching and batching strategies are applied."
            ),
            keywords=[
                "rag",
                "evaluation",
                "hallucination",
                "benchmark",
                "question answering",
            ],
            author="Carol Nguyen",
            publish_date=datetime(2024, 9, 21, 15, 0, 0),
            download_date=datetime(2024, 9, 22, 10, 20, 0),
            total_tokens=3500,
            unique_tokens=900,
            text_length=16000,
        ),
        Document(
            file_id="doc_notes_005",
            title="Design Review Minutes: RAG-based Knowledge Assistant",
            summary=(
                "Meeting minutes from the design review for a RAG-based internal knowledge assistant, "
                "including decisions, open questions, and follow-up items."
            ),
            content=(
                "These minutes summarize the architecture review meeting for the new RAG-based knowledge assistant. "
                "We discussed document ingestion pipelines, metadata enrichment, retrieval strategies (BM25 vs dense), "
                "and prompt design for the answer generation step. The team agreed to start with a hybrid retriever, "
                "implement guardrails for personally identifiable information, and run an A/B test against the existing "
                "FAQ chatbot before full rollout."
            ),
            keywords=[
                "rag",
                "meeting minutes",
                "knowledge assistant",
                "hybrid retrieval",
                "guardrails",
            ],
            author="Design Review Board",
            publish_date=datetime(2024, 7, 5, 13, 30, 0),
            download_date=datetime(2024, 7, 5, 14, 5, 0),
            total_tokens=1500,
            unique_tokens=500,
            text_length=7000,
        ),
    ]


class Generator(metaclass=SingletonMeta):
    """
    问答生成器实例 (单例)

    功能包括：
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
        self._client: Optional[OpenAI] = OpenAI(
            api_key=API_KEY,
            base_url=answer_generator_config.base_url,
        )

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
            results.append(
                {
                    "doc_id": r.doc_id,
                    "title": r.title,
                    "relevance_percent": f"{r.relevance:.2f}%",
                    "summary": r.summary,
                    # "key_fields_summary": r.key_fields_summary,
                    "high_freq_terms": ", ".join(
                        [f"{k}:{v}" for k, v in r.high_freq_terms.items()]
                    ),
                }
            )
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
        if not isinstance(self._client, OpenAI) or API_KEY.strip() == "":
            return {"error": "QA without api key"}

        context_text = self._build_context_from_results(self._current_query_results)
        prompt = self._build_llm_prompt(
            query=self._current_demand_raw, context=context_text
        )

        try:
            resp: ChatCompletion = self._client.chat.completions.create(
                model=answer_generator_config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=answer_generator_config.max_tokens,
                temperature=answer_generator_config.temperature,
            )
            if isinstance(resp.choices[0].message.content, str):
                reply_text: str = resp.choices[0].message.content.strip()
            else:
                reply_text = "(LLM returned non-text content)"
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
            answer_generator_config.model = model
        if max_tokens is not None:
            answer_generator_config.max_tokens = max_tokens
        if api_key is not None:
            answer_generator_config.api_key = api_key
        if temperature is not None:
            answer_generator_config.temperature = temperature
        if base_url is not None:
            answer_generator_config.base_url = base_url
        self._client = OpenAI(
            api_key=API_KEY,
            base_url=answer_generator_config.base_url,
        )
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
        file_keywords = [
            "file",
            "document",
            "doc",
            "list",
            "show",
            "open",
            "report",
            "pdf",
            "find",
            "search",
        ]
        qa_keywords = [
            "why",
            "how",
            "explain",
            "difference",
            "compare",
            "what is",
            "what's",
        ]

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
                model=answer_generator_config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4,
                temperature=0.0,
            )
            if isinstance(resp.choices[0].message.content, str):
                reply_text: str = resp.choices[0].message.content.strip()
            else:
                reply_text = "(LLM returned non-text content)"

            raw = reply_text
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
                    summary=doc.summary,
                    # key_fields_summary=self._summarize_key_fields(doc),
                    high_freq_terms=self._extract_high_freq_terms(doc, query_tokens),
                )
            )

        # 按相关性排序
        results.sort(key=lambda x: x.relevance, reverse=True)
        return results

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
You are an enterprise internal knowledge-base assistant. You can ONLY use the information in the following DOCUMENTS to answer the user's question.
If the documents do not contain enough information, you MUST answer: "No valid reference."

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


# ========================================================================================================================#
# ========================================================================================================================#

# 1. query - 分类 - 查相似度 - 返回文件
# 2. FILE: 结束
# 3. QA: 文件id - summary/... - api - 返回回答


def answer_generator(user_queries=None) -> list[tuple[str, str]]:
    service = Generator()

    if user_queries is None:
        user_queries = [
            "Find me documents about RAG-based LLM question answering system design.",
            "What is the difference between RAG and standard LLM QA? Please explain based on documents.",
            "Show me the company policy for 2025.",
            "Explain the Transformer architecture.",
        ]

    answers: list[tuple[str, str]] = []
    for q in user_queries:

        service.set_demand(q)
        resp = service.get_LLM_reply()

        if resp.get("type") == "file_query":
            all_doc = ""
            for item in resp.get("results", []):
                all_doc += f"{item['title']} (relevance={item['relevance_percent']})"
                all_doc += "\n"
            answers.append(("FILE", all_doc))
        else:
            answers.append(("QA", resp.get("reply", "")))

    return answers
