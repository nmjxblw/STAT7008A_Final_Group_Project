from concurrent.futures import thread
import json
from typing import Any
from crawler_module import crawler, State  # 在模块导入时实例化全局爬虫类，单例模式
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块
import sys
import threading

crawler_bp = Blueprint(
    "crawler_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""爬虫蓝图模块"""


@crawler_bp.route("/setup_crawler_config", methods=["POST"])
def crawler_bp_setup_crawler_config():
    """设置爬虫配置"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到设置爬虫配置请求")
    try:
        request_dict = request.get_json()
        if request_dict is None:
            abort(400, description="✖ 请求数据无效")
        elif isinstance(request_dict, dict):
            config_data = request_dict.get("message")
        else:
            abort(400, description="✖ 请求数据格式错误")
        if not isinstance(config_data, dict):
            abort(400, description="✖ 请求数据格式错误")
        logger.debug(f"爬虫配置请求数据: {config_data}")
        _flag = crawler.update_crawler_config(**config_data)
        response_data = {"status": "success", "message": f"爬虫配置更新结果: {_flag}"}
        logger.debug(f"✔ 爬虫配置更新处理完成，结果: {_flag}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 爬虫配置更新失败: {e}")
        abort(500, description="✖ 设置爬虫配置失败")


@crawler_bp.route("/crawling_task", methods=["POST"])
def crawler_bp_start_crawling_task() -> Any:
    """启动爬虫任务"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到爬虫任务请求")
    try:
        request_data: dict[str, Any] = request.get_json()
        if request_data is None:
            abort(400, description="✖ 请求数据无效")
        logger.debug(f"爬虫任务请求数据: {request_data}")
        command: str = request_data.get("message", "start")
        command = command.lower()
        if command == "pause":
            crawler.pause()
            response_data = {"status": "success", "message": "爬虫任务已暂停"}
        elif command == "resume":
            crawler.resume()
            response_data = {"status": "success", "message": "爬虫任务已恢复"}
        elif command == "stop":
            crawler.stop()
            response_data = {"status": "success", "message": "爬虫任务已停止"}
        else:  # 默认启动爬虫任务
            if crawler.current_state == State.CRAWLING:
                response_data = {"status": "success", "message": "爬虫任务已经在执行中"}
            else:
                response_data = {"status": "success", "message": "爬虫任务开始执行"}
                _thread = threading.Thread(
                    target=crawler.start_crawling_task, daemon=True
                )
                _thread.start()

        return jsonify(response_data)
    except Exception as e:
        abort(500, description="✖ 启动爬虫任务失败")
        raise e


@crawler_bp.route("/get_current_crawling_web", methods=["GET", "POST"])
def crawler_bp_get_current_crawling_web() -> Any:
    """获取当前爬虫网页"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取当前爬虫网页请求")
    try:
        current_web: str = crawler.get_current_crawling_web()
        response_data = {
            "status": "success",
            "current_crawling_web": current_web,
        }
        logger.debug(f"✔ 获取当前爬虫网页成功: {current_web}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 获取当前爬虫网页失败: {e}")
        abort(500, description="✖ 获取当前爬虫网页失败")


@crawler_bp.route("/get_current_crawling_article", methods=["GET", "POST"])
def crawler_bp_get_current_crawling_article() -> Any:
    """获取当前爬虫文章标题"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取当前爬虫文章标题请求")
    try:
        current_article: str = crawler.get_current_crawling_article()
        response_data = {
            "status": "success",
            "current_crawling_article": current_article,
        }
        logger.debug("✔ 获取当前爬虫文章标题成功")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 获取当前爬虫文章标题失败: {e}")
        abort(500, description="✖ 获取当前爬虫文章标题失败")


@crawler_bp.route("/get_crawling_task_progress", methods=["GET", "POST"])
def crawler_bp_get_crawling_task_progress() -> Any:
    """获取爬虫任务进度"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取爬虫任务进度请求")
    try:
        progress: float = crawler.get_crawling_task_progress()
        response_data = {
            "status": "success",
            "crawling_task_progress": progress,
        }
        logger.debug(f"✔ 获取爬虫任务进度成功: {progress}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 获取爬虫任务进度失败: {e}")
        abort(500, description="✖ 获取爬虫任务进度失败")


@crawler_bp.route("/get_block_list", methods=["GET", "POST"])
def crawler_bp_get_block_list() -> Any:
    """获取屏蔽网址列表"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取屏蔽网址列表请求")
    try:
        block_list: list[str] = crawler.get_block_list()
        response_data = {
            "status": "success",
            "block_list": block_list,
        }
        logger.debug(f"✔ 获取屏蔽网址列表成功: {block_list}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 获取屏蔽网址列表失败: {e}")
        abort(500, description="✖ 获取屏蔽网址列表失败")


@crawler_bp.route("/", methods=["GET", "POST"])
def crawler_bp_main() -> Any:
    """爬虫蓝图主入口"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到请求")
    if request.method == "POST":
        return crawler_bp_setup_crawler_config()
    return jsonify({"message": "欢迎来到爬虫蓝图主入口"})
