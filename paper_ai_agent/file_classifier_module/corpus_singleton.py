import os
import pickle
from pathlib import Path
from pymupdf import Document
from utility_module import SingletonMeta


class CorpusSingleton(metaclass=SingletonMeta):  # 请确保这里使用了您的单例元类
    """
    使用单例模式管理的语料库管理器。
    负责语料库的加载、添加文档、检索和持久化。
    """

    def __init__(self, corpus_filename="bm25_corpus.pkl"):
        """
        初始化语料库管理器。单例模式确保此方法只执行一次。

        Args:
            corpus_filename: 语料库持久化文件名
        """
        # 获取项目根目录并确定语料库文件完整路径
        project_root = Path(__file__).parent.parent  # 请根据您的项目结构调整
        self.bm25_folder = project_root / "DB" / "BM25"
        self.bm25_folder.mkdir(parents=True, exist_ok=True)  # 确保目录存在

        self.corpus_path = self.bm25_folder / corpus_filename
        self._corpus: list = []  # 内部变量，存储实际的语料库数据

        # 单例初始化：在实例化时自动加载已有语料库
        self._load_corpus()

    def _load_corpus(self):
        """从文件加载语料库到内存。如果文件不存在，则初始化一个空列表。"""
        try:
            if self.corpus_path.exists():
                with open(self.corpus_path, "rb") as f:
                    self._corpus = pickle.load(f)
                print(
                    f"已从 {self.corpus_path} 加载语料库，包含 {len(self._corpus)} 个文档。"
                )
            else:
                self._corpus = []
                print("未找到现有语料库文件，已初始化一个空语料库。")
        except Exception as e:
            print(f"加载语料库时出错: {e}。将初始化一个空语料库。")
            self._corpus = []

    def add_document(self, document_data):
        """
        向语料库添加或更新一个文档。

        Args:
            document_data (dict): 要添加的文档数据，必须包含 'file_id' 等唯一标识符。
        """
        # 检查文档是否已存在（基于 file_id）
        file_id = document_data.get("file_id")
        if not isinstance(self._corpus, list):
            raise ValueError("语料库数据结构异常，预期为列表。")
        existing_index = next(
            (i for i, doc in enumerate(self._corpus) if doc.get("file_id") == file_id),
            None,
        )

        if existing_index is not None:
            # 更新已存在的文档
            self._corpus[existing_index] = document_data
            print(f"更新了文档: {document_data.get('file_name', 'Unknown')}")
        else:
            # 添加新文档
            self._corpus.append(document_data)
            print(f"添加了新文档: {document_data.get('file_name', 'Unknown')}")

        # 添加或更新后，可以选择自动保存
        self.save_corpus()

    def get_corpus(self):
        """
        获取当前的语料库数据。

        Returns:
            list: 语料库文档列表。
        """
        return self._corpus

    def save_corpus(self):
        """将当前的语料库保存到文件。"""
        try:
            with open(self.corpus_path, "wb") as f:
                pickle.dump(self._corpus, f)
            print(f"语料库已保存至 {self.corpus_path}。")
        except Exception as e:
            print(f"保存语料库时出错: {e}")

    def get_document_by_id(self, file_id: str) -> dict | None:
        """
        根据文件ID查找文档。

        Args:
            file_id: 要查找的文档ID。

        Returns:
            dict or None: 找到的文档，未找到则返回 None。
        """
        if not isinstance(self._corpus, list):
            return None
        for doc in self._corpus:
            if not isinstance(doc, dict):
                continue
            if doc.get("file_id") == file_id:
                return doc
        return None

    def __len__(self):
        """返回语料库中的文档数量。"""
        if not isinstance(self._corpus, list):
            return 0
        return len(self._corpus)
