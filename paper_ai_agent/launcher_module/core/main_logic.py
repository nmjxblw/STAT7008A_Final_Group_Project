"""
主要逻辑模块

在这里处理flask_app的初始化、蓝图注册等主要逻辑
"""

from flask import Flask, Blueprint
from log_module import *  # 导入全局日志模块


def register_blueprints(_flask_app: Flask):
    """注册所有蓝图到flask应用"""
    # 循环注册所有蓝图
    from ..flask_config import blueprints

    for module_path, bp_name, url_prefix in blueprints:
        try:
            logger.debug(f"正在注册蓝图[{bp_name}] 来自模块: {{{module_path}}}")
            # 动态导入模块
            module = __import__(module_path, fromlist=[bp_name])
            # 获取蓝图对象
            blueprint: Blueprint = getattr(module, bp_name)
            if not isinstance(blueprint, Blueprint):
                raise TypeError(f"[{bp_name}] 不是一个有效的Flask蓝图对象")
            logger.debug(f"✔ 蓝图[{bp_name}]加载成功")
            # 注册到应用
            _flask_app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.debug(f'✔ 注册蓝图[{bp_name}] 成功！ Url前缀: "{url_prefix}"')
        except Exception as e:
            logger.debug(f"✘ 注册蓝图[{bp_name}]失败")
            raise e
