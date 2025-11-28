"""
主要逻辑模块

在这里处理flask_app的初始化、蓝图注册等主要逻辑
"""

import re
from flask import Flask, Blueprint
from flask_cors import CORS
from log_module import *
from global_module import AUTO_CRAWL
import threading
import atexit


def register_blueprints(_flask_app: Flask):
    """注册所有蓝图到flask应用"""
    # 循环注册所有蓝图
    logger.debug("正在注册所有Flask蓝图...")
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
    logger.debug("✔ 所有Flask蓝图注册完成。")


def setup_registry():
    """设置开机启动项"""
    from ..registry_module import add_to_startup, is_in_startup, remove_from_startup

    logger.debug("正在处理开机启动项设置...")
    _flag: bool = is_in_startup()
    if not _flag and AUTO_CRAWL:
        success = add_to_startup()
        if success:
            logger.debug("✔ 程序已添加到开机启动项，自动爬取功能已启用。")
        else:
            logger.debug("✘ 无法将程序添加到开机启动项，请检查权限。")
    elif _flag and not AUTO_CRAWL:
        success = remove_from_startup()
        if success:
            logger.debug("✔ 程序已从开机启动项移除，自动爬取功能已禁用。")
        else:
            logger.debug("✘ 无法将程序从开机启动项移除，请检查权限。")
    else:
        logger.debug("开机启动项设置无需更改。")


def setup_scheduler():
    """设置任务调度器"""
    logger.debug("正在设置任务调度器...")
    if AUTO_CRAWL:
        # 启动任务调度器
        from ..scheduler_module import task_scheduler

        task_scheduler.start_scheduling()
        logger.debug("✔ 任务调度器已启动，自动爬取功能已启用。")
    else:
        logger.debug("✘ 自动爬取功能未启用，任务调度器未启动。")


def setup_flask_app(_flask_app: Flask):
    """设置Flask应用"""

    from global_module import HOST, PORT

    atexit.register(on_exit)
    # 启用CORS支持
    CORS(_flask_app)
    logger.debug("✔ CORS已启用")

    logger.debug("启动 Flask 应用...")
    _flask_app.run(
        debug=True, host=HOST, port=PORT, load_dotenv=True, use_reloader=False
    )
    logger.debug("Flask 应用已终止，正在等待其他线程加入...")
    current_thread = threading.current_thread()  # 获取当前线程（通常是主线程）
    _thread_list: list[threading.Thread] = threading.enumerate()
    for t in _thread_list:
        if t is not current_thread:
            t.join(timeout=5.0)


def on_exit():
    """程序退出时的处理函数"""
    logger.debug("主程序退出程序...")
