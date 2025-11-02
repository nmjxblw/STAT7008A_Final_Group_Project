"""启动模块"""

import os
from pathlib import Path
import flask
import threading
from global_module import (
    system_config,
    crawler_config,
    answer_generator_config,
    file_classifier_config,
    ProjectName,
)  # 导入全局变量模块
from crawling_module import *
from launcher_module.core import *
from log_module import logger

_launcher_app: flask.Flask = flask.Flask(f"{ProjectName}")
"""flask应用实例"""

_crawler_instance: WebCrawler = WebCrawler()
"""网页爬虫单例实例"""

_db_handler_instance: DBHandler = DBHandler()
"""数据库处理器单例实例"""


def main():
    """程序入口函数"""
    logger.debug("主程序启动程序...")
    global _crawler_instance, _db_handler_instance, _launcher_app


if __name__ == "__main__":
    main()
