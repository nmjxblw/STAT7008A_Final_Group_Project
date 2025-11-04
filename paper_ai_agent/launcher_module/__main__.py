"""启动器主模块"""

from pathlib import Path
from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy
from global_module import (
    HOST,
    PORT,
    PROJECT_NAME,
)  # 导入全局变量模块
from log_module import *  # 导入全局日志模块


def create_app(
    _config: object | str = "launcher_module.flask_config.DevelopmentFlaskConfig",
) -> Flask:
    """
    创建Flask并绑定数据库

    参数：
        config (object|str): 配置对象或配置路径, 默认为开发配置
    返回：
        _app (Flask): Flask应用实例
    """

    logger.debug("正在创建Flask应用并绑定数据库...")
    _app = Flask(f"{PROJECT_NAME}")
    _app.config.from_object(_config)
    global flask_database
    flask_database.init_app(_app)
    return _app


def get_app() -> Flask:
    """获取flask应用实例"""
    global launcher_app
    if launcher_app is None:
        launcher_app = create_app()
    return launcher_app


def get_database() -> SQLAlchemy:
    """获取flask数据库ORM实例"""
    global flask_database
    if flask_database is None:
        flask_database = SQLAlchemy()
    return flask_database


def run() -> None:
    """程序运行函数"""
    logger.debug("主程序启动程序...")
    from .core.main_logic import (
        create_tables,
        register_blueprints,
    )

    create_tables(get_app())
    register_blueprints(get_app())
    get_app().run(debug=True, host=HOST, port=PORT, load_dotenv=True)
    logger.debug("主程序退出程序...")


flask_database: SQLAlchemy = SQLAlchemy()
"""flask框架数据库ORM实例"""

launcher_app: Flask = create_app()
"""flask应用实例"""

if __name__ == "__main__":
    run()
