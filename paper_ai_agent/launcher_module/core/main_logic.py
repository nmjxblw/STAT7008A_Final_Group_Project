"""
主要逻辑模块

TODO:在这里处理flask_app的初始化、蓝图注册、数据库表创建等主要逻辑
"""

from ..__main__ import _flask_database
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from global_module import PROJECT_NAME, DATABASE_PATH
from pathlib import Path
import log_module

logger = log_module.get_default_logger()
""" 全局日志记录器对象 """


class File(_flask_database.Model):
    """文件模型类，表示存储在数据库中的文件信息"""

    __tablename__ = "file"

    file_id = _flask_database.Column(_flask_database.Integer, primary_key=True)
    """ 文件ID """
    title = _flask_database.Column(_flask_database.String(256), nullable=True)
    """ 文件标题 """
    summary = _flask_database.Column(_flask_database.Text, nullable=True)
    """ 文件摘要 """
    content = _flask_database.Column(_flask_database.Text, nullable=True)
    """ 文件内容 """
    keywords = _flask_database.Column(_flask_database.Text, nullable=True)
    """ 文件关键词 """
    author = _flask_database.Column(_flask_database.String(50), nullable=True)
    """ 文件作者 """
    publish_date = _flask_database.Column(_flask_database.DateTime, nullable=True)
    """ 文件发布日期 """
    download_date = _flask_database.Column(_flask_database.DateTime, nullable=True)
    """ 文件下载日期 """
    total_tokens = _flask_database.Column(_flask_database.Integer, nullable=True)
    """ 文件总令牌数 """
    unique_tokens = _flask_database.Column(_flask_database.Integer, nullable=True)
    """ 文件唯一令牌数 """
    text_length = _flask_database.Column(_flask_database.Integer, nullable=True)
    """ 文件文本长度 """

    def __repr__(self) -> str:
        return f"<File id={self.file_id} title={self.title} author={self.author} publish_date={self.publish_date}>"


def create_app(
    config: (
        object | str
    ) = "launcher_module.config.flask_config_module.DevelopmentFlaskConfig",
) -> Flask:
    """创建并返回Flask应用实例"""
    _app = Flask(f"{PROJECT_NAME}")
    _app.config.from_object(config)
    _flask_database.init_app(_app)
    return _app


def create_tables(_flask_app: Flask):
    """创建数据库表"""
    try:
        logger.debug(f"开始创建表，数据库路径: {DATABASE_PATH} ")
        # 在应用上下文中创建所有表
        with _flask_app.app_context():
            _flask_database.create_all()
        logger.debug("✔ 数据库表创建完成")
    except Exception as e:
        logger.debug(f"✘ 创建表失败: {e}")
        raise e


def register_blueprints(_flask_app: Flask):
    """注册所有蓝图到flask应用"""
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
            _flask_app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.debug(f"✔ 注册蓝图: {bp_name} Url前缀: {url_prefix}")
        except Exception as e:
            logger.debug(f"✘ 注册蓝图失败: {bp_name}")
            raise e
