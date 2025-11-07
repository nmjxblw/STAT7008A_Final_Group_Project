import os
import atexit
from langchain_community.vectorstores import FAISS

class FAISSVectorStoreSingleton:
    """
    FAISS 向量数据库单例类（集成atexit自动保存）。
    """
    _instance = None
    _vector_db = None
    _embeddings_model = None
    _save_path = None
    _initialized = False  # 用于标记是否已初始化atexit注册，避免重复注册

    def __new__(cls, embeddings_model=None, save_path=None):
        """
        确保类只有一个实例。
        在创建实例时接收嵌入模型和保存路径，为懒加载做准备。
        """
        if cls._instance is None:
            cls._instance = super(FAISSVectorStoreSingleton, cls).__new__(cls)
            # 保存配置信息，用于后续的懒加载初始化
            if embeddings_model is not None and save_path is not None:
                cls._instance._embeddings_model = embeddings_model
                cls._instance._save_path = save_path
                os.makedirs(save_path, exist_ok=True) # 确保目录存在
                # 注册退出处理函数，确保只注册一次
                atexit.register(cls._instance._auto_save_on_exit)
                print("faiss单例实例已创建，退出自动保存函数已注册。")
        return cls._instance

    def _lazy_initialize(self, docs=None):
        """
        懒加载初始化向量数据库。
        docs: 仅在需要创建新索引时提供。
        """
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
            print("检测到现有索引文件，已加载。")
        else:
            # 首次创建索引，此时必须提供docs
            if docs is None:
                raise ValueError("索引文件不存在，必须先使用add_documents提供文档(docs)以创建新索引。")
            self._vector_db = FAISS.from_documents(docs, self._embeddings_model)
            print("未找到现有索引，已从文档创建新索引。")
        # 标记初始化完成
        self._initialized = True



    def add_documents(self, docs):
        """向现有向量数据库中添加文档。"""
        if not self._initialized:
            # 这会确保向量库已初始化
            self._lazy_initialize(docs)
        else:
            self._vector_db.add_documents(docs)
        # 注意：添加文档后不立即保存，由退出时统一保存以提高性能
        print(f"已添加 {len(docs)} 个文档到索引（更改暂存于内存）。")

    def similarity_search_with_score(self, query, k=4):
        """
        执行相似性搜索并返回文档及其分数。
        分数为L2距离，越低表示越相似
        """
        if not self._initialized or self._vector_db is None:
            self._lazy_initialize()
        return self._vector_db.similarity_search_with_score(query, k=k)

    def _auto_save_on_exit(self):
        """
        atexit模块注册的退出处理函数。
        在程序退出前自动调用，保存向量数据库索引。
        """
        if self._vector_db is not None and self._initialized:
            self._vector_db.save_local(self._save_path)
            print(f"程序退出，向量索引已自动保存至 {self._save_path}。")
        else:
            print("程序退出，无需保存（向量数据库未初始化或为空）。")

    def manual_save(self):
        """也提供一个手动保存的接口，以备不时之需。"""
        if self._vector_db is not None and self._initialized:
            self._vector_db.save_local(self._save_path)
            print(f"向量索引已手动保存至 {self._save_path}。")
        else:
            print("无需手动保存（向量数据库未初始化或为空）。")