import os
import pickle
from collections import Counter, defaultdict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import DashScopeEmbeddings
import json
from log_module import *  # 导入全局日志模块
from global_module import API_KEY

from .corpus_singleton import CorpusSingleton
from .faiss_singleton import FAISSVectorStoreSingleton
import math


class PDFRagWorker:
    def __init__(self, embedding_model=None):
        """初始化PDFRagWorker

        Args:
            use_local_embedding: 是否使用本地embedding模型
                - True: 使用本地HuggingFace模型（需下载，但免费）
                - False: 使用DashScope API（需API key，但更快）
        """

        self.embedding_model = embedding_model

        self.detected_language: str = "en"  # 检测到的语言（默认按照英文处理）

    def run(self, input_queue, output_queue):
        """
        这个接口为数据流处理预留
        """

    def set_retrieval_knowledge(self, previous_file_data_dict):
        """
        在这里将原文进行语义转换和存储
        """

        # 这里基于embedding和faiss存储
        self.__pdf_split_and_embed(previous_file_data_dict)

        # 使用bm25进行词频统计和存储
        self.__build_bm25_index(previous_file_data_dict)

    def __detect_language(self, text, sample_size=2000):
        """检测文本语言（中文/英文）

        Args:
            text: 待检测文本
            sample_size: 采样大小

        Returns:
            'zh' 或 'en'
        """
        if not text:
            return "en"  # 默认英文

        # 采样前sample_size字符
        sample = text[:sample_size]

        # 统计中文字符数量
        chinese_chars = len([c for c in sample if "\u4e00" <= c <= "\u9fff"])
        total_chars = len(sample)

        # 如果中文字符占比>20%，认为是中文文档
        if total_chars > 0 and (chinese_chars / total_chars) > 0.2:
            return "zh"
        else:
            return "en"

    def __get_api_embedding_model(self):
        """获取embedding模型（根据语言自动选择合适模型）

        Returns:
            api_embeddings_model: 使用api调用的embedding对象
        """

        # 使用API（默认或降级）
        logger.debug("使用DashScope API进行Embedding")
        api_key = API_KEY

        if not api_key:
            logger.debug("警告: DASHSCOPE_API_KEY 未设置")
            logger.debug("请设置环境变量或在代码中配置API key")

        embeddings_model = DashScopeEmbeddings(
            model="text-embedding-v4",
            dashscope_api_key=api_key,
        )
        return embeddings_model

    def __pdf_split_and_embed(self, previous_file_data_dict):

        logger.debug(f'开始尝试对{previous_file_data_dict["file_name"]}进行切分')

        # 1. 获取文档切分
        splitted_docs = self.__content_split(previous_file_data_dict)

        # 2. 进行embedding
        # 这里需要维护一个后端全局的vector_db,要能在后端程序启动时加载,后端程序结束时保存.这里先暂时写为运行到这行代码时加载,运行结束后释放
        self.__embed(splitted_docs)

    def __content_split(self, previous_file_data_dict):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 块大小
            chunk_overlap=200,  # 块重叠
            separators=["\n\n", "\n", ".", "!", "?", " "],  # 分隔符
        )

        doc = Document(
            page_content=previous_file_data_dict[
                "file_text"
            ],  # 这是已经从PDF提取并清理的文本
            metadata={
                "file_name": previous_file_data_dict["file_name"],
                "file_id": previous_file_data_dict["file_id"],
                "file_title": previous_file_data_dict["file_title"],
                "file_summary": previous_file_data_dict["file_summary"],
                "file_keywords": ", ".join(
                    previous_file_data_dict["file_keywords"]
                ),  # 将关键词列表转为字符串
            },
        )
        # 2. 文本分割
        splitted_doc = text_splitter.split_documents([doc])
        return splitted_doc

    def __embed(self, docs):
        # 项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # faiss文件保存目录
        save_embed_folder = os.path.join(project_root, "DB", "embedding")
        # 获取embedding模型（支持本地和API两种方式）
        if self.embedding_model is None:
            logger.warning("实例化PDFRagWorker时未传入本地embeeding模型，fallback调用api模型")
            self.embeddings_model = self.__get_api_embedding_model()
        vector_store = FAISSVectorStoreSingleton(self.embedding_model, save_embed_folder)

        vector_store.add_documents(docs)

    def get_faiss_retrieval(self, query, k):
        embeddings_model = self.embedding_model
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # faiss文件保存目录
        save_embed_folder = os.path.join(project_root, "DB", "embedding")
        vector_store = FAISSVectorStoreSingleton(embeddings_model, save_embed_folder)
        return vector_store.similarity_search_with_score(query, k)

    def get_bm25_retrieval(self, query, k=10, score_threshold=0.0):
        """从BM25索引中检索最相关的k条记录

        Args:
            query: 查询文本
            k: 返回的最相关文档数量
            score_threshold: 分数阈值，只返回高于此阈值的结果

        Returns:
            list: 排序后的结果列表，每个元素为字典包含：
                - document: 文档信息
                - score: 相似度得分
                - rank: 排名
                - file_id: 文件ID
                - file_name: 文件名
        """
        corpus_manager = CorpusSingleton()
        corpus = corpus_manager.get_corpus()
        if not corpus:
            logger.warning("BM25语料库为空，无法进行检索")
            return []

        # 对查询进行分词
        query_terms = self.__tokenize_text(query)
        if not query_terms:
            logger.warning("查询分词结果为空")
            return []

        logger.debug(f"查询分词结果: {query_terms}")

        # 预先计算语料库统计信息
        if not hasattr(self, "doc_freq"):
            self._calculate_corpus_statistics(corpus)

        # 为每个文档计算BM25得分
        results = []
        for doc in corpus:
            score = self._calculate_bm25_score(query_terms, doc, corpus)

            if score > score_threshold:
                results.append(
                    {
                        "document": doc,
                        "score": score,
                        "file_id": doc["file_id"],
                        "file_name": doc["file_name"],
                        "matched_terms": self._find_matched_terms(
                            query_terms, doc.get("tokens", [])
                        ),
                    }
                )

        # 按得分降序排序
        results.sort(key=lambda x: x["score"], reverse=True)

        # 添加排名信息
        for i, result in enumerate(results[:k]):
            result["rank"] = i + 1

        logger.debug(
            f"BM25检索完成: 查询='{query}', 返回 {len(results[:k])} 个结果 (总分: {len(results)})"
        )

        return results[:k]

    def _find_matched_terms(self, query_terms, doc_tokens):
        """找出查询中与文档匹配的词项"""
        return [term for term in query_terms if term in doc_tokens]

    def __build_bm25_index(self, previous_file_data_dict):
        """构建BM25索引并进行词频统计

        将文档分词后存储到BM25语料库，并统计高频词。

        Args:
            previous_file_data_dict: 包含文件信息的字典
                - file_id: 文件唯一标识
                - file_text: 文件文本内容
                - file_name: 文件名
                - file_keywords: 关键词列表

        Returns:
            None (结果保存到文件系统)

        Storage:
            - DB/bm25/corpus.pkl: BM25语料库（包含所有文档的分词结果）
            - DB/bm25/term_freq.json: 词频统计结果
        """
        try:
            logger.debug(f'开始对{previous_file_data_dict["file_name"]}构建BM25索引')

            # 1. 文本分词
            tokens = self.__tokenize_text(previous_file_data_dict["file_text"])

            if not tokens:
                logger.debug("警告: 分词结果为空，跳过BM25索引构建")
                return

            # 2. 词频统计
            term_frequency = self.__calculate_term_frequency(tokens)

            # 3. 加载或创建语料库（存储在DB/BM25目录下）
            corpus_manager = CorpusSingleton()

            # 4. 添加新文档到语料库
            doc_entry = {
                "file_id": previous_file_data_dict["file_id"],
                "file_name": previous_file_data_dict["file_name"],
                "tokens": tokens,  # 分词结果
                "term_frequency": term_frequency,  # 词频统计
                "metadata": {
                    "file_title": previous_file_data_dict.get("file_title", ""),
                    "file_summary": previous_file_data_dict.get("file_summary", ""),
                    "file_keywords": previous_file_data_dict.get("file_keywords", []),
                },
            }

            corpus_manager.add_document(doc_entry)

            corpus = corpus_manager.get_corpus()

            # 6. 保存词频统计到JSON（便于查看）- 这部分可以保留
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bm25_folder = os.path.join(project_root, "DB", "BM25")
            os.makedirs(bm25_folder, exist_ok=True)

            term_freq_path = os.path.join(bm25_folder, "term_freq.json")

            # 加载现有词频统计
            if os.path.exists(term_freq_path):
                with open(term_freq_path, "r", encoding="utf-8") as f:
                    all_term_freq = json.load(f)
            else:
                all_term_freq = {}

            # 更新词频统计
            all_term_freq[previous_file_data_dict["file_id"]] = {
                "file_name": previous_file_data_dict["file_name"],
                "top_terms": term_frequency[:50],  # 保存前50个高频词
                "total_tokens": len(tokens),
                "unique_tokens": len(set(tokens)),
            }

            # 保存
            with open(term_freq_path, "w", encoding="utf-8") as f:
                json.dump(all_term_freq, f, ensure_ascii=False, indent=2)

            logger.debug(f"BM25索引构建完成，当前语料库文档数: {len(corpus)}")
            logger.debug(f"文档词数: {len(tokens)}, 独特词数: {len(set(tokens))}")
            logger.debug(f"Top 10 高频词: {[term for term, _ in term_frequency[:10]]}")

        except Exception as e:
            logger.debug(f"BM25索引构建失败: {e}")
            raise e

    def __get_stop_words(self, language="en"):
        """获取停用词表

        Args:
            language: 'zh' 或 'en'

        Returns:
            set: 停用词集合
        """
        if language == "zh":
            # 中文停用词表
            stop_words = {
                "的",
                "了",
                "在",
                "是",
                "我",
                "有",
                "和",
                "就",
                "不",
                "人",
                "都",
                "一",
                "一个",
                "上",
                "也",
                "很",
                "到",
                "说",
                "要",
                "去",
                "你",
                "会",
                "着",
                "没有",
                "看",
                "好",
                "自己",
                "这",
                "那",
                "里",
                "来",
                "他",
                "她",
                "它",
                "们",
                "为",
                "与",
                "及",
                "对",
                "把",
                "被",
                "从",
                "以",
                "向",
                "用",
                "于",
                "将",
                "让",
                "给",
                "而",
                "则",
                "或",
                "且",
                "但",
                "却",
                "因",
                "所",
                "因为",
                "所以",
                "如果",
                "虽然",
                "然而",
                "因此",
                "并且",
                "还是",
                "或者",
                "不是",
                "这个",
                "那个",
                "什么",
                "怎么",
                "为什么",
                "哪里",
                "谁",
                "多少",
                "几",
                "些",
                "每",
                "比",
                "更",
                "最",
                "非常",
                "特别",
                "已",
                "已经",
                "正在",
                "曾",
                "曾经",
            }
        else:
            # 英文停用词表（包含连词、代词、介词、be动词等）
            stop_words = {
                # 冠词
                "a",
                "an",
                "the",
                # be动词
                "is",
                "am",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                # 助动词
                "do",
                "does",
                "did",
                "will",
                "would",
                "shall",
                "should",
                "may",
                "might",
                "can",
                "could",
                "must",
                "ought",
                "have",
                "has",
                "had",
                # 代词
                "i",
                "you",
                "he",
                "she",
                "it",
                "we",
                "they",
                "them",
                "their",
                "theirs",
                "my",
                "mine",
                "your",
                "yours",
                "his",
                "her",
                "hers",
                "its",
                "our",
                "ours",
                "this",
                "that",
                "these",
                "those",
                "who",
                "whom",
                "whose",
                "which",
                "what",
                "myself",
                "yourself",
                "himself",
                "herself",
                "itself",
                "ourselves",
                "themselves",
                # 介词
                "in",
                "on",
                "at",
                "by",
                "for",
                "with",
                "about",
                "against",
                "between",
                "into",
                "through",
                "during",
                "before",
                "after",
                "above",
                "below",
                "to",
                "from",
                "up",
                "down",
                "out",
                "off",
                "over",
                "under",
                "again",
                "further",
                "then",
                "once",
                "of",
                # 连词
                "and",
                "but",
                "or",
                "nor",
                "so",
                "yet",
                "as",
                "if",
                "when",
                "where",
                "while",
                "because",
                "although",
                "though",
                "since",
                "unless",
                "until",
                # 其他常见词
                "not",
                "no",
                "yes",
                "all",
                "any",
                "both",
                "each",
                "few",
                "more",
                "most",
                "other",
                "some",
                "such",
                "only",
                "own",
                "same",
                "than",
                "too",
                "very",
                "just",
                "now",
                "here",
                "there",
                "how",
                "why",
            }

        return stop_words

    def __tokenize_text(self, text):
        """对文本进行分词（根据语言选择分词工具）

        中文使用jieba分词，英文使用空格分词+标点处理。
        自动过滤停用词。

        Args:
            text: 待分词的文本

        Returns:
            list: 分词后的词语列表（已过滤停用词）
        """
        try:
            import re

            if not text:
                return []

            # 获取停用词表
            stop_words = self.__get_stop_words(self.detected_language)

            # 根据语言选择分词方法
            if self.detected_language == "zh":
                # 中文：使用jieba分词
                try:
                    import jieba

                    tokens = jieba.lcut(text)
                except ImportError:
                    logger.debug("警告: jieba未安装，中文分词效果将受影响")
                    tokens = text.split()
            else:
                # 英文：使用正则分词（按单词边界分割）
                # 保留字母和数字组成的单词
                tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())

            # 过滤：去除停用词、单字符、纯数字、纯标点
            filtered_tokens = []
            for token in tokens:
                token = token.strip().lower()

                # 基本长度过滤
                if len(token) < 2:
                    continue

                # 停用词过滤
                if token in stop_words:
                    continue

                # 过滤纯数字
                if token.isdigit():
                    continue

                # 中文特殊标点过滤
                if all(c in '，。！？、；：""' "【】（）《》" for c in token):
                    continue

                filtered_tokens.append(token)

            return filtered_tokens

        except Exception as e:
            logger.debug(f"分词失败: {e}")
            # 降级方案：简单空格分词
            return [
                word.strip().lower() for word in text.split() if len(word.strip()) > 1
            ]

    def __calculate_term_frequency(self, tokens):
        """计算词频统计

        Args:
            tokens: 分词列表

        Returns:
            list: [(词语, 频次), ...] 按频次降序排列
        """
        if not tokens:
            return []

        # 使用Counter统计词频
        term_counts = Counter(tokens)

        # 按频次降序排序
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)

        return sorted_terms

    def _calculate_bm25_score(self, query_terms, doc, corpus):
        """计算查询与文档的BM25相关性得分

        Args:
            query_terms: 查询词项列表
            doc: 文档数据（包含tokens和元数据）

        Returns:
            float: BM25得分
        """
        try:
            # 获取文档的分词结果
            doc_tokens = doc.get("tokens", [])
            if not doc_tokens:
                return 0.0

            # 获取文档长度
            doc_length = len(doc_tokens)

            # 计算平均文档长度（如果尚未计算）
            if not hasattr(self, "avg_doc_length"):
                self._calculate_corpus_statistics(corpus)

            # BM25参数（可调整）
            k1 = 1.5  # 词频饱和度参数，通常范围[1.2, 2.0]
            b = 0.75  # 文档长度归一化参数，通常范围[0.5, 0.8]

            score = 0.0

            for term in query_terms:
                # 跳过不在文档中的词项
                if term not in doc_tokens:
                    continue

                # 计算词项在文档中的频率(TF)
                term_frequency = doc_tokens.count(term)

                # 计算逆文档频率(IDF)
                idf = self._calculate_idf(term, corpus)
                if idf <= 0:
                    continue

                # BM25公式计算
                numerator = term_frequency * (k1 + 1)
                denominator = term_frequency + k1 * (
                        1 - b + b * (doc_length / self.avg_doc_length)
                )

                term_score = idf * (numerator / denominator)
                score += term_score

            return score

        except Exception as e:
            logger.debug(f"BM25得分计算失败: {e}")
            return 0.0

    def _calculate_idf(self, term, corpus):
        """计算词项的逆文档频率(IDF)

        Args:
            term: 词项

        Returns:
            float: IDF值
        """
        if not hasattr(self, "doc_freq"):
            self._calculate_corpus_statistics(corpus)

        # 如果词项不在语料库中，返回0
        if term not in self.doc_freq:
            return 0

        # 包含该词项的文档数
        n_qi = self.doc_freq[term]
        # 总文档数
        N = len(corpus)

        # 标准BM25 IDF公式（避免除零）
        idf = math.log((N - n_qi + 0.5) / (n_qi + 0.5) + 1.0)
        return idf

    def _calculate_corpus_statistics(self, corpus):
        """计算语料库统计信息（文档频率、平均文档长度等）"""
        if not corpus:
            self.doc_freq = {}
            self.avg_doc_length = 0
            return

        # 计算文档频率（每个词项出现在多少文档中）
        self.doc_freq = defaultdict(int)
        total_length = 0

        for doc in corpus:
            doc_tokens = doc.get("tokens", [])
            total_length += len(doc_tokens)

            # 每个文档中每个词项只计一次（使用set去重）
            unique_terms = set(doc_tokens)
            for term in unique_terms:
                self.doc_freq[term] += 1

        # 计算平均文档长度
        self.avg_doc_length = total_length / len(corpus) if corpus else 0
