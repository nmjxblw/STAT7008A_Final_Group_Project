"""启动器主模块"""

from pathlib import Path
from flask import Blueprint, Flask

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

    logger.debug("正在创建Flask应用实例...")
    _app = Flask(f"{PROJECT_NAME}")

    # 修改 Jinja2 定界符以避免与 Vue.js 语法冲突
    # Jinja2 使用 {[ ]},Vue.js 使用 {{ }}
    _app.jinja_env.variable_start_string = "{["
    _app.jinja_env.variable_end_string = "]}"
    _app.jinja_env.comment_start_string = "{#"
    _app.jinja_env.comment_end_string = "#}"

    _app.config.from_object(_config)
    return _app


def run() -> None:
    """程序运行函数"""
    logger.debug("主程序启动程序...")
    from .core.main_logic import (
        register_blueprints,
    )

    global launcher_app
    register_blueprints(launcher_app)
    launcher_app.run(
        debug=True, host=HOST, port=PORT, load_dotenv=True, use_reloader=False
    )
    logger.debug("主程序退出程序...")


launcher_app: Flask = create_app()
"""flask应用实例"""
