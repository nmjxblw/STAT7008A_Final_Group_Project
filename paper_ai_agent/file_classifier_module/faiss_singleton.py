import os
import atexit
from typing import Optional
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from utility_module import SingletonMeta
from log_module import logger


class FAISSVectorStoreSingleton(metaclass=SingletonMeta):
    """
    FAISS 向量数据库单例类（集成atexit自动保存）。
    """

    _vector_db: FAISS
    """ FAISS向量数据库实例，类级别属性。 """
    _embeddings_model: Embeddings
    """ 嵌入模型实例，类级别属性。 """
    _save_path: str
    """ 向量数据库保存路径，类级别属性。 """
    _initialized = False  # 用于标记是否已初始化atexit注册，避免重复注册
    """ 标记是否已初始化向量数据库实例。 """

    def __init__(self, embeddings_model: Embeddings, save_path: str) -> None:
        """初始化函数，实际初始化在需要时进行（懒加载）。

        参数:
            embeddings_model (Embeddings): 用于向量化的嵌入模型实例
            save_path (str): 向量数据库保存路径
        """
        if embeddings_model is not None and save_path is not None:
            self._embeddings_model = embeddings_model
            self._save_path = save_path
            os.makedirs(save_path, exist_ok=True)  # 确保目录存在
            # 注册退出处理函数，确保只注册一次
            try:
                atexit.register(self._auto_save_on_exit)
                logger.debug("FAISS向量数据库自动保存方法注册成功。")
            except Exception as e:
                logger.error(f"FAISS向量数据库自动保存方法注册失败：{e}")
        else:
            logger.warning(
                "self初始化时embeddings_model或save_path为None，某些功能可能无法使用"
            )

    def _lazy_initialize(self, docs: list[Document] | None = None):
        """
        懒加载初始化向量数据库。
        docs: 仅在需要创建新索引时提供。
        """
        # 检查必要的属性是否已初始化
        if self._embeddings_model is None or self._save_path is None:
            raise ValueError(
                "self未正确初始化：embeddings_model或save_path为None，无法进行懒加载初始化"
            )

        if self._vector_db is not None:
            return  # 已经初始化，直接返回

        index_file = os.path.join(self._save_path, "index.faiss")
        if os.path.exists(index_file):
            # 加载现有索引
            self._vector_db = FAISS.load_local(
                self._save_path,
                self._embeddings_model,
                allow_dangerous_deserialization=True,
            )
            logger.debug("检测到现有索引文件，已加载。")
            record_count = self._vector_db.index.ntotal
            logger.debug(f"当前索引数量：{record_count}")
        else:
            # 首次创建索引，此时必须提供docs
            if not docs:
                raise ValueError(
                    "索引文件不存在，必须先使用add_documents提供文档(docs)以创建新索引。"
                )
            self._vector_db = FAISS.from_documents(docs, self._embeddings_model)
            logger.debug("未找到现有索引，已从文档创建新索引。")
            record_count = self._vector_db.index.ntotal
            logger.debug(f"当前索引数量：{record_count}")
        # 标记初始化完成
        self._initialized = True

    def add_documents(self, docs: list[Document]):
        """向现有向量数据库中添加文档。"""
        if not self._initialized:
            # 这会确保向量库已初始化
            self._lazy_initialize(docs)
        else:
            assert self._vector_db is not None, "向量数据库未初始化"
            self._vector_db.add_documents(docs)
        # 注意：添加文档后不立即保存，由退出时统一保存以提高性能
        logger.debug(f"已添加 {len(docs)} 个文档到索引（更改暂存于内存）。")
        assert self._vector_db is not None, "向量数据库未初始化"
        record_count = self._vector_db.index.ntotal
        logger.debug(f"当前索引数量：{record_count}")

    def similarity_search_with_score(self, query, k=4) -> list[tuple[Document, float]]:
        """
        执行相似性搜索并返回文档及其分数。
        分数为L2距离，越低表示越相似
        """
        # 检查必要的属性是否已初始化
        if self._embeddings_model is None or self._save_path is None:
            raise ValueError(
                "FAISSVectorStoreSingleton未正确初始化：embeddings_model或save_path为None"
            )

        if not self._initialized or self._vector_db is None:
            self._lazy_initialize()

        logger.debug(f"正在进行FAISS Retrieval检索")
        assert self._vector_db is not None, "向量数据库未初始化"
        return self._vector_db.similarity_search_with_score(query, k=k)

    def _auto_save_on_exit(self):
        """
        atexit模块注册的退出处理函数。
        在程序退出前自动调用，保存向量数据库索引。
        """
        if self._vector_db is not None and self._initialized:
            record_count = self._vector_db.index.ntotal

            self._vector_db.save_local(self._save_path)
            logger.debug(
                f"程序退出，向量索引已自动保存至 {self._save_path}。当前有{record_count}个索引。"
            )
        else:
            logger.debug("程序退出，无需保存（向量数据库未初始化或为空）。")

    def manual_save(self):
        """也提供一个手动保存的接口，以备不时之需。"""
        if self._vector_db is not None and self._initialized:
            self._vector_db.save_local(self._save_path)
            logger.debug(f"向量索引已手动保存至 {self._save_path}。")
        else:
            logger.debug("无需手动保存（向量数据库未初始化或为空）。")
