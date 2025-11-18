import enum
import os
from pathlib import Path
from typing import Optional
from global_module import RESOURCE_DIR, CLASSIFIED_DIR, UNCLASSIFIED_DIR
from log_module import logger
import threading


class _State(enum.Enum):
    """文件分类任务状态枚举类"""

    IDLE = "IDLE"
    """ 空闲状态 """
    RUNNING = "RUNNING"
    """ 运行中状态 """
    PAUSED = "PAUSED"
    """ 暂停状态 """


_resume_event = threading.Event()
"""恢复事件，用于控制文件分类任务的暂停和恢复"""
_resume_event.set()  # 初始状态为非暂停

_stop_event = threading.Event()
"""停止事件，用于控制文件分类任务的终止"""
_stop_event.clear()  # 清除停止状态，表示任务未停止


def start_file_classify_task(
    unclassified_path: Path = UNCLASSIFIED_DIR,
    classified_path: Path = CLASSIFIED_DIR,
    file_type: str = "pdf",
    file_name: Optional[str] = None,
) -> bool:
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
    global _current_state
    if _current_state == _State.RUNNING:
        logger.debug("文件分类任务已经在执行中...")
        return True
    elif _current_state == _State.PAUSED:
        resume_file_classify_task()
        return True
    else:
        _current_state = _State.RUNNING
        logger.debug("文件分类任务正在启动...")
        _stop_event.clear()  # 重置停止事件
        _resume_event.set()  # 确保任务未暂停

    from .pdf_analysis import PDFContentAnalyzer
    from .pdf_split_and_embed import PDFRagWorker
    from .pdf_transform import PDFTransformer
    from .utils import save_to_database, move_files, get_local_embedding_model

    # 这里先以单文件为例顺序执行,后续可以实现根据流式处理的多线程调度

    # pdf转换,目前实现转文字,且未筛选有效信息
    # 优化文理,优化正则匹配效果,剔除无用信息; OCR
    if file_type != "pdf":
        raise RuntimeError("当前只能处理pdf")
    unclassified_path = Path.joinpath(unclassified_path, file_type.upper())
    unclassified_path.mkdir(parents=True, exist_ok=True)
    classified_path.mkdir(parents=True, exist_ok=True)

    file_name_list = []

    if file_name is None:
        for file_in_dir in os.listdir(unclassified_path):  # 仅当前目录
            # 在每个耗时任务开始前检查停止事件
            if _stop_event.is_set():
                logger.debug("文件分类任务已停止...")
                return False
            _resume_event.wait()
            # 过滤系统文件和隐藏文件
            if file_in_dir.startswith(".") or file_in_dir == "DS_Store":
                continue
            if file_in_dir.endswith(file_type):
                file_name_list.append(file_in_dir)
    else:

        file_name_list.append(file_name)

    # 在每个耗时任务开始前检查停止事件
    if _stop_event.is_set():
        logger.debug("文件分类任务已停止...")
        return False
    _resume_event.wait()

    embedding_model = get_local_embedding_model()

    for name in file_name_list:
        if _stop_event.is_set():
            logger.debug("文件分类任务已停止...")
            break
        _resume_event.wait()
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
            "keywords": pdf_info_dict.get(
                "file_keywords", []
            ),  # 传递列表，让database_module处理
            "author": "",
            "text_length": len(pdf_info_dict["file_text"]),
            "file_name": pdf_info_dict["file_name"],
        }

        # 保存到数据库
        if save_to_database(save_dict):
            logger.info(
                f"文件分类任务：文件 {pdf_info_dict['file_name']} 已成功保存到数据库"
            )
            # 移动已处理的文件到已分类目录
            move_files(unclassified_path, classified_path, [name])
        else:
            logger.error(
                f"文件分类任务：文件 {pdf_info_dict['file_name']} 保存到数据库失败"
            )

    _stop_event.clear()  # 任务完成后设置停止事件
    _resume_event.set()  # 确保线程不会因为暂停而阻塞
    _current_state = _State.IDLE
    return True


def pause_file_classify_task():
    """暂停文件分类任务"""

    global _current_state
    _current_state = _State.PAUSED

    _stop_event.clear()
    _resume_event.clear()

    logger.debug("文件分类任务已暂停...")


def resume_file_classify_task():
    """恢复文件分类任务"""

    global _current_state
    _current_state = _State.RUNNING

    _stop_event.clear()
    _resume_event.set()

    logger.debug("文件分类任务已恢复...")


def stop_file_classify_task():
    """停止文件分类任务"""
    global _current_state
    _current_state = _State.IDLE

    _stop_event.set()
    _resume_event.set()  # 确保线程不会因为暂停而阻塞

    logger.debug("文件分类任务已停止...")


def run():
    """运行文件分类任务（使用默认路径）"""

    start_file_classify_task()


def test_retrieval():
    from .utils import get_retrieval_content

    get_retrieval_content("what is computer vision?", 10)


_current_state: _State = _State.IDLE
"""当前文件分类任务状态"""
