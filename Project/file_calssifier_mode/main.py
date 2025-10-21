

from Project.file_calssifier_mode.pdf_analysis import PDFContentAnalyser
from Project.file_calssifier_mode.pdf_split_and_embed import PDFRagWorker
from Project.file_calssifier_mode.pdf_transform import PDFTransformer
from Project.file_calssifier_mode.utils import save_to_json, move_files


def start_file_classify_task(unclassified_path, file_name ,classified_path, json_db_path):


    """
    目前数据格式如下
        "file_id",
        "file_text",
        "file_name",
        "file_title",
        "file_summary",
        "file_keywords",

    """
    #这里先以单文件为例顺序执行,后续可以实现根据流式处理的多线程调度

    #pdf转换,目前实现转文字,且未筛选有效信息
    #TODO:优化文字处理,优化正则匹配效果,剔除无用信息; OCR
    transformer=PDFTransformer()
    pdf_info_dict=transformer.transform(unclassified_path, file_name)

    #pdf分析,目前使用了deepseek api
    analyzer=PDFContentAnalyser()
    pdf_info_dict=analyzer.analyze(pdf_info_dict)

    #rag前期工作,包括embedding和BM25,目前仅有基于embedding api的模型,且数据切分很粗糙,后续需要优化
    #TODO:embedding本地部署调用; BM25实现; Faiss的全局启动(与flask对接); 数据切分方式优化
    ragWorker=PDFRagWorker()
    ragWorker.set_retrival_knowledge(pdf_info_dict)

    #数据入库(键值库,现在先保存到json)
    #TODO:完成数据库的部署和连接
    #save_data()
    save_to_json(pdf_info_dict,json_db_path)
    move_files(unclassified_path,classified_path, [file_name])






