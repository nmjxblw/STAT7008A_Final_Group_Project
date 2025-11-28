import asyncio
import sys
from typing import Any, List, Optional, AsyncGenerator
from openai import OpenAI
from openai.types.chat import ChatCompletion
from langchain_core.documents import Document
from global_module import answer_generator_config, API_KEY
from utility_module import SingletonMeta
from database_module import *
from file_classifier_module.utils import get_retrieval_content
from .utils import DemandType, query_files_by_attributes
from log_module import logger
import numpy as np


class Generator(metaclass=SingletonMeta):
    """
    问答生成器实例 (单例)

    功能包括：
        1. 自动识别意图（文件查询/问答）
        2. 文档搜索与富集
        3. 基于上下文的LLM问答
    """

    def __init__(self):

        self._current_demand_raw: str = ""
        self._current_demand_type: Optional[DemandType] = None
        self._current_query_results: List[tuple[str, float]] = []
        self._stopped: bool = False
        self._prompt: str = ""

        # LLM配置与客户端
        self._client: Optional[OpenAI] = OpenAI(
            api_key=API_KEY,
            base_url=answer_generator_config.base_url,
        )

    # ======================
    # 公共API
    # ======================

    def set_demand(self, user_input: str) -> tuple[str, List[tuple]]:
        """设置用户需求"""
        logger.debug(f"{sys._getframe().f_code.co_name}收到用户需求: {user_input}")
        num_doc = 5
        self._stopped = False
        self._prompt = ""
        self._current_demand_raw = user_input.strip()
        self._current_demand_type = self._classify_demand(user_input)

        if self._current_demand_type == DemandType.FILE_QUERY:
            demand = "file"
        elif self._current_demand_type == DemandType.QA:
            demand = "qa"
        else:
            demand = "file"
        logger.debug(f"识别需求类型: {demand}")

        retrieval: dict[str, list[Any]] = get_retrieval_content(
            self._current_demand_raw,
            k_segments=30,
            k_articles=15,
        )
        segments_retrieval: list[tuple[Document, float]] = retrieval[
            "most_similar_paragrapghs"
        ]
        articles_retrieval: list[dict[str, Any]] = retrieval["most_similar_paper"]

        segment_set: dict[str, float] = {}
        for doc, score in segments_retrieval:
            _id = doc.metadata.get("file_id")
            if _id is None:
                continue
            segment_set[_id] = min(round(float(score), 2), segment_set.get(_id, 100.0))
        # logger.debug(f'FAISS: {segment_set}')
        segment_set = {
            key: round(1 / (1 + np.exp(4 * dist - 5)), 2)
            for key, dist in segment_set.items()
        }
        # segment_set = list(segment_set.items())
        # logger.debug(f'FAISS: {segment_set}')

        article_set: dict[str, float] = {}
        for result in articles_retrieval:
            _id = result.get("file_id")
            score = result.get("score")
            if _id is None or score is None:
                continue
            article_set[_id] = max(round(float(score), 2), article_set.get(_id, 0.0))
        # logger.debug(f'BM25: {article_set}')
        article_set = {
            key: round(1 / (1 + np.exp(3 - score)), 2)
            for key, score in article_set.items()
        }
        # article_set = list(article_set.items())
        # logger.debug(f'BM25: {article_set}')

        candidates = dict()
        threshold = 0.6
        for key, sim in segment_set.items():
            candidates[key] = sim + threshold
        for key, sim in article_set.items():
            if key in candidates:
                candidates[key] *= sim + threshold
            else:
                candidates[key] = sim + threshold
        for key in candidates:
            candidates[key] = round(candidates.get(key, 0.0) / (threshold + 1) ** 2, 2)

        candidates = list(candidates.items())
        # logger.debug(f'candidates: {candidates}')
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:num_doc]
        # logger.debug(f'candidates: {candidates}')

        self._current_query_results = candidates
        return demand, self._current_query_results

    def stop_current_task(self) -> bool:
        """停止当前任务（流式输出时使用）"""
        self._stopped = True
        return True

    def redo_task(self, user_input: str) -> tuple[str, List]:
        """重新运行任务"""
        return self.set_demand(user_input)

    def get_query_result_titles(self) -> List[str]:
        """返回匹配的文档标题列表（用于UI）"""
        titles = []
        for doc in self._current_query_results:
            try:
                file_id = doc[0]
                file = query_files_by_attributes({"file_id": file_id})[0]
                titles.append(file["title"])
            except:
                continue
        return titles

    def get_LLM_reply(self, reference: List[str]) -> str:
        """获取LLM回复"""
        """输入 [file_id] | 输出回答"""

        if not self._current_demand_raw:
            logger.debug("ERROR: no demand set.")
            return "ERROR: no demand set."
        if self._current_demand_type == DemandType.FILE_QUERY:
            logger.debug("ERROR: not in QA mode.")
            return "ERROR: not in QA mode."
        if not isinstance(self._client, OpenAI) or API_KEY.strip() == "":
            logger.debug("ERROR: QA without api key.")
            return "ERROR: QA without api key."

        self._prompt = self._build_llm_prompt(
            query=self._current_demand_raw,
            files=reference,
            use_content=False,
        )

        try:
            resp: ChatCompletion = self._client.chat.completions.create(
                model=answer_generator_config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self._prompt},
                ],
                max_tokens=answer_generator_config.max_tokens,
                temperature=answer_generator_config.temperature,
            )
            if isinstance(resp.choices[0].message.content, str):
                reply_text: str = resp.choices[0].message.content.strip()
            else:
                reply_text = "(大语言模型返回了非文本内容)"
        except Exception as e:
            logger.debug(f"大语言模型回答失败: {e}")
            raise e
        return reply_text

    # ======================
    # 内部方法：意图识别
    # ======================

    def _classify_demand(self, user_input: str) -> DemandType:
        """set_demand调用"""
        """分类用户需求类型"""
        # 优先用LLM分类
        llm_label = self._classify_with_llm(user_input)
        if llm_label == "FILE":
            return DemandType.FILE_QUERY
        if llm_label == "QA":
            return DemandType.QA

        # raise Exception("API_KEY在.env中未设置，无法使用LLM进行意图分类")

        # 关键字 fallback
        logger.debug(
            f"{sys._getframe().f_code.co_name}: LLM_QUERY_CLASSIFICATION_ERROR"
        )
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

        return DemandType.QA if has_qa else DemandType.FILE_QUERY

    def _classify_with_llm(self, user_input: str) -> Optional[str]:
        """set_demand调用_classify_demand调用"""
        """用LLM进行意图分类"""
        if not self._client:
            logger.debug("ERROR: no client.")
            raise Exception("No LLM client available.")

        system_prompt = (
            "You are an intent classifier. "
            "You must answer with EXACTLY ONE WORD: 'FILE' or 'QA'. "
            "Do NOT explain.\n"
            "- If the user wants to search/list/view/find/open documents/files/reports -> answer FILE.\n"
            "- If the user asks for explanation/analysis/how-to/reasoning -> answer QA.\n"
            "- If it is mixed, prefer QA."
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
            if raw in ("FILE", "QA"):
                return raw
            logger.debug("ERROR: unexpected demand type.")
            return None
        except Exception:
            logger.debug(
                f"ERROR: client errors | api_key: {self._client.api_key} | base_url: {self._client.base_url}"
            )
            return None

    # ======================
    # 内部方法：Prompt构建
    # ======================

    def _build_llm_prompt(self, query: str, files: List[str], use_content=False) -> str:
        """构建LLM提示词"""
        reference = []
        for file_id in files:
            try:
                file = query_files_by_attributes({"file_id": file_id})[0]
                content = file["summary"]
                if use_content:
                    content += file["content"]
                reference.append(f"[{file['file_id']}]\n{content}\n")
            except:
                continue
        context = "\n".join(reference)
        return f"""
You are an enterprise internal knowledge-base assistant.
You should follow the ANSWERING RULES to answer the user's question.

[ANSWERING RULES]
1. You can ONLY use the information in the following DOCUMENTS.
2. Each document starts with its DOCUMENT_ID contained in square brackets.
3. When you cite a document, add its DOCUMENT_ID in square brackets at the end of the sentence, e.g. [DOCUMENT_ID].
4. If multiple documents mention the same thing, you can cite multiple DOCUMENT_ID, e.g. [DOCUMENT_ID_1][DOCUMENT_ID_2].

[DOCUMENTS]
{context}

[USER QUESTION]
{query}

Start answering now:
""".strip()
