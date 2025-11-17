import os
import shutil
from typing import Any
from log_module import logger


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
        logger.debug(f"✖ 文件移动操作失败: {e}")
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

        logger.info(f"✔ 已删除 {deleted_count} 个已处理的文件")
        return True

    except Exception as e:
        logger.error(f"✖ 文件删除操作失败: {e}")
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


def get_retrieval_content(query: str, k_segments: int = 20, k_articles: int = 5):
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
    from .pdf_split_and_embed import PDFRagWorker
    
    embedding_model = get_local_embedding_model()
    worker = PDFRagWorker(embedding_model)
    faiss_retrieval = worker.get_faiss_retrieval(query, k_segments)
    bm25_retrieval = worker.get_bm25_retrieval(query, k_articles)
    retrieval = {
        "most_similar_paragrapghs": faiss_retrieval,
        "most_similar_paper": bm25_retrieval,
    }
    return retrieval


def get_local_embedding_model():
    # 使用本地HuggingFace模型
    logger.debug("获取本地Embedding模型")
    try:
        # 优先使用新版本的langchain-huggingface包，否则回退到旧版本
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)
        
        import os.path

        # 根据检测到的语言选择模型

        model_name = "sentence-transformers/all-MiniLM-L6-v2"  # 英文模型，约90MB
        logger.debug(f"  选择模型: {model_name}")

        # 检查模型是否已下载
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        model_dir_name = f"models--{model_name.replace('/', '--')}"
        model_path = os.path.join(cache_dir, model_dir_name)

        if os.path.exists(model_path):
            logger.debug(f"  本地模型已缓存: {model_path}")
        else:
            logger.debug(f"  本地模型未找到，开始自动下载...")
            logger.debug(f"  模型大小: { '~90MB'}")
            logger.debug(f"  下载位置: {cache_dir}")

        # 加载模型（如果不存在会自动下载）
        embeddings_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},  # 使用CPU，如有GPU可改为'cuda'
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.debug(f"本地模型加载成功: {model_name}")
        return embeddings_model

    except Exception as e:
        logger.debug(f"本地模型加载失败: {e}")
        logger.debug("首次使用需要下载模型，请确保网络连接")
        logger.debug("或安装: pip install sentence-transformers")
        return None
