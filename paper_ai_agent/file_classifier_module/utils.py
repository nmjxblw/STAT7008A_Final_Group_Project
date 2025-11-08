import json
import os
import shutil
from typing import Any
from log_module import *

from paper_ai_agent.file_classifier_module.pdf_split_and_embed import PDFRagWorker


def move_files(source, target, success_filename_list):
    """
    根据文件名列表，将源文件夹中存在的对应文件移动到目标文件夹
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


def save_to_json(file_info, save_data_folder):
    """将结果保存到简单的文件数据库中"""
    # 如果数据库文件已存在，加载现有数据
    db_file = os.path.join(save_data_folder, "pdf_analysis_database.json")
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            database = json.load(f)
    else:
        database = {}
    # 使用文件名作为键，保存完整元数据和文本
    database[file_info["file_name"]] = {
        "file_id": file_info["file_id"][:8],  # 只保存前8位
        "file_name": file_info["file_name"],
        "title": file_info["file_title"],  # 键名改为title
        "summary": file_info["file_summary"],
        "keywords": file_info["file_keywords"],
        "full_text": file_info["file_text"],  # 保存完整文本
        "text_length": len(file_info["file_text"]),  # 文本长度统计
    }

    # 保存到JSON文件
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)


async def save_to_database(file_dic: dict[str, Any]) -> bool:
    """
    异步操作，将文件信息保存到flask数据库中
    """
    # 延迟导入以避免循环依赖
    from launcher_module.core.database_operations import add_or_update_file_to_database

    return await add_or_update_file_to_database(file_dic)




def get_retrieval_content(query:str,k:int):
    worker=PDFRagWorker()
    faiss_retrieval=worker.get_faiss_retrieval(query,k)
    bm25_retrieval=worker.get_bm25_retrieval(query,k)
    retrieval={
        "most_similar_paragrapghs":faiss_retrieval,
        "most_similar_paper":bm25_retrieval
    }
    return retrieval
