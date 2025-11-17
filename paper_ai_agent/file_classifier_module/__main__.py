import os
from pathlib import Path
from log_module import logger


def start_file_classify_task(
    unclassified_path, classified_path, file_type, file_name=None
) -> None:
    """
    文件分类任务主函数
    
    处理流程：
        1. PDF转换提取文本
        2. AI分析生成标题、摘要、关键词
        3. RAG处理（embedding + BM25索引）
        4. 保存到数据库
        5. 移动文件到已分类目录
        
    数据格式：
        "file_id": 文件MD5哈希ID
        "title": 文件标题
        "summary": 文件摘要
        "content": 文件全文内容
        "keywords": 关键词列表（存储时用|分隔）
        "author": 作者（当前为空）
        "text_length": 文本长度
        "file_name": 文件名
    """
    from .pdf_analysis import PDFContentAnalyzer
    from .pdf_split_and_embed import PDFRagWorker
    from .pdf_transform import PDFTransformer
    from .utils import save_to_database, move_files, get_local_embedding_model

    # 这里先以单文件为例顺序执行,后续可以实现根据流式处理的多线程调度

    # pdf转换,目前实现转文字,且未筛选有效信息
    # TODO:优化文理,优化正则匹配效果,剔除无用信息; OCR

    if file_type != "pdf":
        raise RuntimeError("当前只能处理pdf")
    file_name_list = []

    if file_name is None:
        for file_in_dir in os.listdir(unclassified_path):  # 仅当前目录
            if file_in_dir.endswith(file_type):
                file_name_list.append(file_in_dir)
    else:
        file_name_list.append(file_name)

    embedding_model = get_local_embedding_model()

    for name in file_name_list:
        transformer = PDFTransformer()
        pdf_info_dict = transformer.transform(unclassified_path, name)

        # pdf分析,目前使用了deepseek api
        analyzer = PDFContentAnalyzer()
        pdf_info_dict = analyzer.analyze(pdf_info_dict)

        # rag前期工作,包括embedding和BM25,目前仅有基于embedding api的模型,且数据切分很粗糙,后续需要优化
        ragWorker = PDFRagWorker(embedding_model=embedding_model)  # 明确指定本地模型
        ragWorker.set_retrieval_knowledge(pdf_info_dict)

        # 构建数据库保存格式 - 严格按照database_module的File模型要求
        save_dict: dict = {
            "file_id": pdf_info_dict["file_id"],
            "title": pdf_info_dict.get("file_title", ""),
            "summary": pdf_info_dict.get("file_summary", ""),
            "content": pdf_info_dict["file_text"],
            "keywords": pdf_info_dict.get("file_keywords", []),  # 传递列表，让database_module处理
            "author": "",
            "text_length": len(pdf_info_dict["file_text"]),
            "file_name": pdf_info_dict["file_name"],
        }

        # 保存到数据库
        if save_to_database(save_dict):
            logger.info(
                f"✔ 文件分类任务：文件 {pdf_info_dict['file_name']} 已成功保存到数据库"
            )
            # 移动已处理的文件到已分类目录
            move_files(unclassified_path, classified_path, [name])
        else:
            logger.error(
                f"✖ 文件分类任务：文件 {pdf_info_dict['file_name']} 保存到数据库失败"
            )


def run():
    """运行文件分类任务（使用默认路径）"""
    # 使用Path进行跨平台路径处理
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    resource_dir = parent_dir / "Resource"
    unclassified_dir = resource_dir / "Unclassified"  # 直接在Unclassified下
    classified_dir = resource_dir / "Classified"
    
    # 确保目录存在
    unclassified_dir.mkdir(parents=True, exist_ok=True)
    classified_dir.mkdir(parents=True, exist_ok=True)
    
    start_file_classify_task(str(unclassified_dir), str(classified_dir), "pdf")


def test_retrieval():
    from .utils import get_retrieval_content

    get_retrieval_content("what is computer vision?", 10)
