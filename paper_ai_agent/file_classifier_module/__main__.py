import os


def start_file_classify_task(
        unclassified_path, classified_path, file_type, file_name=None
) -> None:
    """
    目前数据格式如下
        "file_id",
        "file_text",
        "file_name",
        "file_title",
        "file_summary",
        "file_keywords",

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

        # 数据入库(键值库,现在先保存到json)

        save_dict={
            "file_id":pdf_info_dict["file_id"],
            "title":pdf_info_dict["file_title"],
            "summary": pdf_info_dict["file_summary"],
            "content":pdf_info_dict["file_text"],
            "keywords":','.join(pdf_info_dict["file_keywords"]),
            "author":"",
            "text_length":len(pdf_info_dict["file_text"]),
            "file_name":pdf_info_dict["file_name"],
        }

        if save_to_database(save_dict):
            from paper_ai_agent.log_module import logger
            import sys

            logger.info(
                f"✔ {sys._getframe().f_code.co_name}:文件{pdf_info_dict['file_name']}保存到数据库成功"
            )
            move_files(unclassified_path, classified_path, [name])


def run():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir_A = os.path.dirname(current_dir)
    resource_dir = os.path.abspath(os.path.join(parent_dir_A, 'Resource'))
    unclassified_dir = os.path.abspath(os.path.join(resource_dir, 'unclassified/PDF/'))
    classified_dir = os.path.abspath(os.path.join(resource_dir, 'Classified'))
    start_file_classify_task(unclassified_dir, classified_dir, "pdf")


def test_retrieval():
    from .utils import get_retrieval_content
    get_retrieval_content("what is computer vision?", 10)
