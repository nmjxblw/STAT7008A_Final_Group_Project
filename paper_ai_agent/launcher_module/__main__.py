"""启动器主模块"""

from pathlib import Path

from lark import logger
from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy
import flask
from global_module import (
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


_flask_database: SQLAlchemy = SQLAlchemy()
"""数据库ORM实例"""


def main(_flask_app: Flask) -> None:
    """程序入口函数"""
    logger.debug("主程序启动程序...")
    global _crawler_instance, _flask_database, _launcher_app
    create_tables(_flask_app)
    register_blueprints(_flask_app)
    _flask_app.run(debug=True, host=HOST, port=PORT, load_dotenv=True)
    logger.debug("主程序退出程序...")


_launcher_app: Flask = create_app()
"""flask应用实例"""

if __name__ == "__main__":
    main(_launcher_app)
