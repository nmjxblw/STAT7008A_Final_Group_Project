"""启动模块"""

import os
from pathlib import Path
import pathlib
import flask
import threading
import json
from global_mode.global_dynamic_object import (
    system_config,
    crawler_config,
    logging_config,
    answer_generator_config,
    file_classifier_config,
)  # 导入全局变量模块
import crawling_mode
from .core import *
from log_mode import logger
import utility_mode

launcher_app = flask.Flask("launcher_app")
"""flask应用实例"""

_crawler_instance = crawling_mode.WebCrawler()

_db_handler_instance = DBHandler()
"""数据库处理器单例实例"""


def main():
    """程序入口函数"""
    logger.debug("启动程序...")
    logger.info(f"项目名称: {system_config.project_name}")
    # 在此处添加程序的主要逻辑
    threading.Event().wait(1)  # 模拟一些工作
    raise Exception("测试异常日志记录")
    logger.debug(f"程序终止！")


if __name__ == "__main__":
    main()
