"""
主要逻辑模块

TODO:在这里处理flask_app的初始化、蓝图注册、数据库表创建等主要逻辑
"""

from flask import Flask, Blueprint
from log_module import *  # 导入全局日志模块


def create_tables(_flask_app: Flask):
    """创建数据库表"""
    from global_module import DATABASE_PATH

    try:
        logger.debug(f"开始创建表，数据库路径: {DATABASE_PATH} ")
        # 在应用上下文中创建所有表
        with _flask_app.app_context():
            from ..__main__ import flask_database

            flask_database.create_all()
        logger.debug("✔ 数据库表创建完成")
    except Exception as e:
        logger.debug(f"✘ 创建表失败: {e}")
        raise e


def register_blueprints(_flask_app: Flask):
    """注册所有蓝图到flask应用"""
    # 循环注册所有蓝图
    from flask_config import blueprints

    for module_path, bp_name, url_prefix in blueprints:
        try:
            logger.debug(f"正在注册蓝图: {bp_name} 来自模块: {module_path}...")
            # 动态导入模块
            module = __import__(module_path, fromlist=[bp_name])
            # 获取蓝图对象
            blueprint: Blueprint = getattr(module, bp_name)
            if not isinstance(blueprint, Blueprint):
                raise TypeError(f"{bp_name} 不是一个有效的Flask蓝图对象")
            logger.debug(f"✔ 蓝图模块导入成功: {bp_name}")
            # 注册到应用
            _flask_app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.debug(f'✔ 注册蓝图: {bp_name} 成功！ Url前缀: "{url_prefix}"')
        except Exception as e:
            logger.debug(f"✘ 注册蓝图失败: {bp_name}")
            raise e
