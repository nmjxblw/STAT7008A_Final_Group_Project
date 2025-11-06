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


def run() -> None:
    """程序运行函数"""
    logger.debug("主程序启动程序...")
    from .core.main_logic import (
        create_tables,
        register_blueprints,
    )

    global launcher_app, flask_database
    create_tables(launcher_app)
    register_blueprints(launcher_app)
    # 为避免 Werkzeug reloader 导致主程序重复运行（父子进程都会执行 __main__），
    # 在开发时如果仍想启用调试输出但不希望进程重复，可关闭自动重载。
    # 如果你希望保留自动重载以便代码改动自动生效，可改用:
    #     if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #         launcher_app.run(...)
    launcher_app.run(
        debug=True, host=HOST, port=PORT, load_dotenv=True, use_reloader=False
    )
    logger.debug("主程序退出程序...")


flask_database: SQLAlchemy = SQLAlchemy()
"""flask框架数据库ORM实例"""

launcher_app: Flask = create_app()
"""flask应用实例"""
