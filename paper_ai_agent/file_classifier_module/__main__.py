def start_file_classify_task(
    unclassified_path, file_name, classified_path, json_db_path
) -> bool:
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
    from .utils import save_to_database, move_files

    # 这里先以单文件为例顺序执行,后续可以实现根据流式处理的多线程调度

    # pdf转换,目前实现转文字,且未筛选有效信息
    # TODO:优化文字处理,优化正则匹配效果,剔除无用信息; OCR
    transformer = PDFTransformer()
    pdf_info_dict = transformer.transform(unclassified_path, file_name)

    # pdf分析,目前使用了deepseek api
    analyzer = PDFContentAnalyzer()
    pdf_info_dict = analyzer.analyze(pdf_info_dict)

    # rag前期工作,包括embedding和BM25,目前仅有基于embedding api的模型,且数据切分很粗糙,后续需要优化
    # TODO:embedding本地部署调用; BM25实现; Faiss的全局启动(与flask对接); 数据切分方式优化
    ragWorker = PDFRagWorker(use_local_embedding=True)  # 明确指定
    ragWorker.set_retrieval_knowledge(pdf_info_dict)

    # 数据入库(键值库,现在先保存到json)
    # TODO:完成数据库的部署和连接
    # save_data()

    if save_to_database(pdf_info_dict):
        from log_module import logger
        import sys

        logger.info(
            f"✔ {sys._getframe().f_code.co_name}:文件{pdf_info_dict['file_name']}保存到数据库成功"
        )
        return move_files(unclassified_path, classified_path, [file_name])
    else:
        return False
