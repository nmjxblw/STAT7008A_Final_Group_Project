"""启动模块"""

from json import load
import os
import sys
from pathlib import Path
import flask
import threading

import test
from global_module import (
    crawler_config,
    answer_generator_config,
    file_classifier_config,
    PROJECT_NAME,
    API_KEY,
    HOST,
    PORT,
)  # 导入全局变量模块
from crawling_module import *
from .core import *
from log_module import logger

_launcher_app: flask.Flask = flask.Flask(f"{PROJECT_NAME}")
"""flask应用实例"""

_crawler_instance: WebCrawler = WebCrawler()
"""网页爬虫单例实例"""

_db_handler_instance: DBHandler = DBHandler()
"""数据库处理器单例实例"""


def main():
    """程序入口函数"""
    logger.debug("主程序启动程序...")
    global _crawler_instance, _db_handler_instance, _launcher_app
    register_blueprints()
    _launcher_app.run(debug=True, host=HOST, port=PORT, load_dotenv=True)


def register_blueprints():
    """注册所有蓝图到flask应用"""
    global _launcher_app
    # 配置蓝图列表： (蓝图对象, URL前缀)
    blueprints = [
        (
            "launcher_module.core.test_blueprint",
            "test_bp",
            "/test",
        ),  # 测试模块，URL前缀为 /test
    ]

    # 循环注册所有蓝图
    for module_path, bp_name, url_prefix in blueprints:
        # 动态导入模块
        module = __import__(module_path, fromlist=[bp_name])
        # 获取蓝图对象
        blueprint = getattr(module, bp_name)
        # 注册到应用
        _launcher_app.register_blueprint(blueprint, url_prefix=url_prefix)
        logger.debug(f"注册蓝图: {bp_name} Url前缀为: {url_prefix}")


if __name__ == "__main__":
    main()
