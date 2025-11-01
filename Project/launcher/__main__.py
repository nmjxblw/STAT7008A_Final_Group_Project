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
from core import *


app_settings_file_name = Path.joinpath(Path.cwd(), "app_settings.json")
"""应用设置文件名"""

launcher_app = flask.Flask("launcher_app")
"""flask应用实例"""

_crawler_instance = crawling_mode.WebCrawler()

_db_handler_instance = DBHandler()
"""数据库处理器单例实例"""


def main():
    """程序入口函数"""


if __name__ == "__main__":
    main()
