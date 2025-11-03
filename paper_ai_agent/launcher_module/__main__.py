"""启动器主模块"""

from json import load
import os
import sys
from pathlib import Path

from lark import logger
from flask import Blueprint
import flask
import threading

import argparse
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
import log_module

logger = log_module.get_default_logger()

_launcher_app: flask.Flask = flask.Flask(f"{PROJECT_NAME}")
"""flask应用实例"""

_crawler_instance: WebCrawler = WebCrawler()
"""网页爬虫单例实例"""

_db_handler_instance: DBHandler = DBHandler()
"""数据库处理器单例实例"""


def main() -> None:
    """程序入口函数"""
    logger.debug("主程序启动程序...")
    global _crawler_instance, _db_handler_instance, _launcher_app
    register_blueprints()
    _launcher_app.run(debug=True, host=HOST, port=PORT, load_dotenv=True)
    logger.debug("主程序退出程序...")


def register_blueprints():
    """注册所有蓝图到flask应用"""
    global _launcher_app
    # 配置蓝图列表： (蓝图对象, URL前缀)
    blueprints = [
        (
            "launcher_module.core.main_blueprint",
            "main_bp",
            "/",
        ),
        (
            "launcher_module.core.example_blueprint",
            "example_bp",
            "/example",
        ),
    ]

    # 循环注册所有蓝图
    for module_path, bp_name, url_prefix in blueprints:
        try:
            logger.debug(f"正在注册蓝图: {bp_name} 来自模块: {module_path}...")
            # 动态导入模块
            module = __import__(module_path, fromlist=[bp_name])
            # 获取蓝图对象
            blueprint: Blueprint = getattr(module, bp_name)
            # 注册到应用
            _launcher_app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.debug(f"✔ 注册蓝图: {bp_name} Url前缀: {url_prefix}")
        except Exception as e:
            logger.debug(f"✘ 注册蓝图失败: {bp_name}")
            raise e


if __name__ == "__main__":
    main()
