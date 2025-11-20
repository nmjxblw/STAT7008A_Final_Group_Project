import os
import shutil
from typing import Any
from langchain_core.documents import Document
from log_module import logger
from utility_module import SingletonMeta


def move_files(source, target, success_filename_list):
    """
    根据文件名列表，将源文件夹中存在的对应文件移动到目标文件夹

    Args:
        source: 源文件夹路径
        target: 目标文件夹路径
        success_filename_list: 需要移动的文件名列表

    Returns:
        bool: 操作是否成功
    """
    try:
        # 检查文件夹
        if not os.path.exists(source):
            raise Exception(f"source folder {source} not exists")

        if not os.path.exists(target):
            os.makedirs(target)

        # 移动文件
        moved_count = 0
        for filename in success_filename_list:
            src_path = os.path.join(source, filename)
            dst_path = os.path.join(target, filename)

            if os.path.exists(src_path):
                shutil.move(src_path, dst_path)
                logger.debug(f"Moved: {filename}")
                moved_count += 1
            else:
                logger.debug(f"Not found: {filename}")

        logger.debug(f"Finished. Moved {moved_count} files")
        return True

    except Exception as e:
        logger.debug(f"文件移动操作失败: {e}")
        return False


def delete_files(source, success_filename_list):
    """
    根据文件名列表，删除源文件夹中的文件（用于分类后清理）

    Args:
        source: 源文件夹路径
        success_filename_list: 需要删除的文件名列表

    Returns:
        bool: 操作是否成功
    """
    try:
        # 检查文件夹
        if not os.path.exists(source):
            raise Exception(f"source folder {source} not exists")

        # 删除文件
        deleted_count = 0
        for filename in success_filename_list:
            src_path = os.path.join(source, filename)

            if os.path.exists(src_path):
                os.remove(src_path)
                logger.debug(f"Deleted: {filename}")
                deleted_count += 1
            else:
                logger.debug(f"Not found: {filename}")

        logger.info(f"已删除 {deleted_count} 个已处理的文件")
        return True

    except Exception as e:
        logger.error(f"文件删除操作失败: {e}")
        return False


def save_to_database(file_dic: dict[str, Any]) -> bool:
    """
    将文件信息保存到flask数据库中

    参数:
        file_dic (dict[str, Any]): 包含文件信息的字典
    返回:
        bool: 保存是否成功
    """
    from database_module import add_or_update_file_to_database

    return add_or_update_file_to_database(file_dic)


def query_files_by_attributes(attributes: dict[str, Any]) -> list[dict[str, Any]]:
    """
    根据指定属性查询文件记录

    参数:
        attributes (dict[str, Any]): 包含查询属性的字典
    返回:
        files (list[dict[str, Any]]): 符合条件的文件列表（字典对象）
    """
    from database_module import query_files_by_attributes

    return query_files_by_attributes(attributes)


def get_retrieval_content(
    query: str, k_segments: int = 20, k_articles: int = 5
) -> dict[str, list[Any]]:
    """
    RAG综合检索接口（FAISS向量相似度检索 + BM25关键词检索）

    这是供其他模块（如answer_generator）调用的主要检索接口。
    结合了两种检索方式，提供更全面的检索结果。

    Args:
        query: 查询字符串
        k_segments: FAISS检索返回的段落数量（默认20）
        k_articles: BM25检索返回的文章数量（默认5）

    Returns:
        dict: 包含两种检索结果的字典
            {
                'most_similar_paragrapghs': [  # FAISS检索结果
                    (Document, score),  # score越小越相似，推荐阈值 < 1.5
                    ...
                ],
                'most_similar_paper': [  # BM25检索结果
                    {
                        'document': {...},
                        'score': float,  # score越大越相关，推荐阈值 > 1.0
                        'rank': int,
                        'file_id': str,
                        'file_name': str,
                        'matched_terms': [str, ...]
                    },
                    ...
                ]
            }

    注意：
        - FAISS分数：越小越相似（距离度量）
        - BM25分数：越大越相关（相关度评分）
        - 两种分数评判标准完全不同，不可直接比较
    """
    if not query or not isinstance(query, str) or not query.strip():
        error_msg = f"查询字符串无效：{query}。查询不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if k_segments <= 0 or k_articles <= 0:
        error_msg = f"检索数量参数无效：k_segments={k_segments}, k_articles={k_articles}。必须大于0"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        from .pdf_split_and_embed import PDFRagWorker
        
        embedding_model = get_local_embedding_model()
        if embedding_model is None:
            error_msg = "无法加载embedding模型进行检索，请检查网络连接或模型安装"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        worker = PDFRagWorker(embedding_model)
        
        # FAISS检索
        try:
            faiss_retrieval: list[tuple[Document, float]] = worker.get_faiss_retrieval(query, k_segments)
        except Exception as e:
            error_msg = f"FAISS检索失败：{type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.debug(f"错误详情：{e}", exc_info=True)
            faiss_retrieval = []  # 返回空列表而不是抛出异常
        
        # BM25检索
        try:
            bm25_retrieval: list[dict[str, Any]] = worker.get_bm25_retrieval(query, k_articles)
        except Exception as e:
            error_msg = f"BM25检索失败：{type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.debug(f"错误详情：{e}", exc_info=True)
            bm25_retrieval = []  # 返回空列表而不是抛出异常
        
        retrieval: dict[str, list[Any]] = {
            "most_similar_paragrapghs": faiss_retrieval,
            "most_similar_paper": bm25_retrieval,
        }
        
        if not faiss_retrieval and not bm25_retrieval:
            logger.warning(f"检索结果为空，查询：{query}。可能原因：数据库中没有文档或查询不匹配")
        
        return retrieval
    except (RuntimeError, ValueError):
        raise
    except Exception as e:
        error_msg = f"RAG检索过程发生未知错误：{type(e).__name__}: {e}"
        logger.error(error_msg)
        logger.debug(f"错误详情：{e}", exc_info=True)
        raise RuntimeError(error_msg) from e


class EmbeddingModelSingleton(metaclass=SingletonMeta):
    """
    Embedding模型单例类

    确保整个程序生命周期内只加载一次embedding模型，避免重复加载浪费内存和时间。
    使用SingletonMeta元类实现单例模式。
    """

    def __init__(self):
        """初始化单例，只在第一次创建实例时执行"""
        self._model = None
        self._model_name = "sentence-transformers/all-MiniLM-L6-v2"
        logger.debug("EmbeddingModelSingleton实例已创建")

    def get_model(self):
        """
        获取embedding模型实例

        第一次调用时加载模型，后续调用直接返回已加载的模型。

        Returns:
            HuggingFaceEmbeddings: embedding模型实例，如果加载失败则返回None
        """
        if self._model is None:
            logger.info("首次加载Embedding模型...")
            try:
                # 优先使用新版本的langchain-huggingface包，否则回退到旧版本
                try:
                    from langchain_huggingface import HuggingFaceEmbeddings
                except ImportError:
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                    import warnings

                    warnings.filterwarnings("ignore", category=DeprecationWarning)

                import os.path

                logger.debug(f"  模型名称: {self._model_name}")

                # 检查模型是否已下载到本地
                cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
                model_dir_name = f"models--{self._model_name.replace('/', '--')}"
                model_path = os.path.join(cache_dir, model_dir_name)

                if os.path.exists(model_path):
                    logger.debug(f"  本地模型已缓存: {model_path}")
                else:
                    logger.debug(f"  本地模型未找到，开始自动下载...")
                    logger.debug(f"  模型大小: ~90MB")
                    logger.debug(f"  下载位置: {cache_dir}")

                # 加载模型（如果不存在会自动下载）
                self._model = HuggingFaceEmbeddings(
                    model_name=self._model_name,
                    model_kwargs={"device": "cpu"},  # 使用CPU，如有GPU可改为'cuda'
                    encode_kwargs={"normalize_embeddings": True},
                )
                logger.info(f"Embedding模型加载成功: {self._model_name}")

            except Exception as e:
                error_msg = f"Embedding模型加载失败：{type(e).__name__}: {e}"
                logger.error(error_msg)
                logger.debug("首次使用需要下载模型，请确保网络连接")
                logger.debug("或安装: pip install sentence-transformers")
                logger.debug(f"错误详情：{e}", exc_info=True)
                return None
        else:
            logger.debug("使用已缓存的Embedding模型实例")

        return self._model


def get_local_embedding_model():
    """
    获取本地embedding模型（单例）

    这是一个便捷函数，内部使用EmbeddingModelSingleton确保模型只加载一次。
    其他模块应该通过这个函数获取embedding模型。

    Returns:
        HuggingFaceEmbeddings: embedding模型实例，如果加载失败则返回None

    Example:
        >>> from file_classifier_module import get_local_embedding_model
        >>> model = get_local_embedding_model()  # 第一次调用，加载模型
        >>> model2 = get_local_embedding_model()  # 第二次调用，直接返回已加载的模型
        >>> assert model is model2  # 是同一个对象
    """
    return EmbeddingModelSingleton().get_model()
