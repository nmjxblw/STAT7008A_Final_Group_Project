"""启动器主模块"""

from json import load
import os
import sys
from pathlib import Path

from lark import logger
from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy
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
    DATABASE_PATH,
)  # 导入全局变量模块
from crawling_module import *
from .core import *
import log_module

logger = log_module.get_default_logger()

_launcher_app: Flask = Flask(f"{PROJECT_NAME}")
"""flask应用实例"""
_launcher_app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{Path.joinpath(Path.cwd(), DATABASE_PATH)}"
)
_launcher_app.config["SQLALCHEMY_RECORD_QUERIES"] = True
_launcher_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
_launcher_app.config["SQLALCHEMY_ECHO"] = True
_database: SQLAlchemy = SQLAlchemy(_launcher_app)
"""数据库ORM实例"""

_crawler_instance: WebCrawler = WebCrawler()
"""网页爬虫单例实例"""


class File(_database.Model):
    """文件模型类，表示存储在数据库中的文件信息"""

    __tablename__ = "file"

    file_id = _database.Column(_database.Integer, primary_key=True)
    """ 文件ID """
    title = _database.Column(_database.String(256), nullable=True)
    """ 文件标题 """
    summary = _database.Column(_database.Text, nullable=True)
    """ 文件摘要 """
    content = _database.Column(_database.Text, nullable=True)
    """ 文件内容 """
    keywords = _database.Column(_database.Text, nullable=True)
    """ 文件关键词 """
    author = _database.Column(_database.String(50), nullable=True)
    """ 文件作者 """
    publish_date = _database.Column(_database.DateTime, nullable=True)
    """ 文件发布日期 """
    download_date = _database.Column(_database.DateTime, nullable=True)
    """ 文件下载日期 """
    total_tokens = _database.Column(_database.Integer, nullable=True)
    """ 文件总令牌数 """
    unique_tokens = _database.Column(_database.Integer, nullable=True)
    """ 文件唯一令牌数 """
    text_length = _database.Column(_database.Integer, nullable=True)
    """ 文件文本长度 """

    def __repr__(self) -> str:
        return f"<File id={self.file_id} title={self.title} author={self.author} publish_date={self.publish_date}>"


def main() -> None:
    """程序入口函数"""
    logger.debug("主程序启动程序...")
    global _crawler_instance, _database, _launcher_app
    create_tables()
    register_blueprints()
    _launcher_app.run(debug=True, host=HOST, port=PORT, load_dotenv=True)
    logger.debug("主程序退出程序...")


def create_tables():
    """创建数据库表"""
    global _database, _launcher_app
    try:
        logger.debug(f"开始创建表，数据库路径: {DATABASE_PATH} ")
        # 在应用上下文中创建所有表
        with _launcher_app.app_context():
            _database.create_all()
        logger.debug("✔ 数据库表创建完成")
    except Exception as e:
        logger.debug(f"✘ 创建表失败: {e}")
        raise e


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
