from concurrent.futures import thread
import json
from typing import Any
from global_module import blueprints
from log_module import *
from crawler_module import *
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path

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
            abort(400, description="✘  请求数据无效")
        elif isinstance(request_dict, dict):
            config_data = request_dict.get("message")
        else:
            abort(400, description="✘  请求数据格式错误")
        if not isinstance(config_data, dict):
            abort(400, description="✘  请求数据格式错误")
        logger.debug(f"爬虫配置请求数据: {config_data}")
        _flag = update_crawler_config(**config_data)
        response_data = {"status": "success", "message": f"爬虫配置更新结果: {_flag}"}
        logger.debug(f"✔ 爬虫配置更新处理完成，结果: {_flag}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✘  爬虫配置更新失败: {e}")
        abort(500, description="✘  设置爬虫配置失败")


@crawler_bp.route("/crawling_task", methods=["POST"])
def crawler_bp_crawling_task() -> Any:
    """启动爬虫任务"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到爬虫任务请求")
    try:
        request_data: dict[str, Any] = request.get_json()
        if request_data is None:
            abort(400, description="✘  请求数据无效")
        logger.debug(f"爬虫任务请求数据: {request_data}")
        command: str = request_data.get("message", "start")
        command = command.lower()
        if command == "pause":
            pause_crawling_task()
            response_data = {"status": "success", "message": "爬虫任务已暂停"}
        elif command == "resume":
            resume_crawling_task()
            response_data = {"status": "success", "message": "爬虫任务已恢复"}
        elif command == "stop":
            stop_crawling_task()
            response_data = {"status": "success", "message": "爬虫任务已停止"}
        else:  # 默认启动爬虫任务
            _thread = threading.Thread(target=start_crawling_task, daemon=True)
            _thread.start()
            response_data = {"status": "success", "message": "爬虫任务开始执行"}

        return jsonify(response_data)
    except Exception as e:
        abort(500, description="✘  启动爬虫任务失败")
        raise e


@crawler_bp.route("/get_current_crawling_web", methods=["GET", "POST"])
def crawler_bp_get_current_crawling_web() -> Any:
    """获取当前爬虫网页"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取当前爬虫网页请求")
    try:
        current_web: str = get_current_crawling_web()
        response_data = {
            "status": "success",
            "message": {"current_crawling_web": current_web},
        }
        logger.debug(f"✔ 获取当前爬虫网页成功: {current_web}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✘  获取当前爬虫网页失败: {e}")
        abort(500, description="✘  获取当前爬虫网页失败")


@crawler_bp.route("/get_current_crawling_article", methods=["GET", "POST"])
def crawler_bp_get_current_crawling_article() -> Any:
    """获取当前爬虫文章标题"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取当前爬虫文章标题请求")
    try:
        current_article: str = get_current_crawling_article()
        response_data = {
            "status": "success",
            "message": {"current_crawling_article": current_article},
        }
        logger.debug("✔ 获取当前爬虫文章标题成功")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✘  获取当前爬虫文章标题失败: {e}")
        abort(500, description="✘  获取当前爬虫文章标题失败")


@crawler_bp.route("/get_visited_urls_count", methods=["GET", "POST"])
def crawler_bp_get_visited_urls_count() -> Any:
    """获取已访问URL数量"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取已访问URL数量请求")
    try:
        count: int = get_visited_urls_count()
        response_data = {
            "status": "success",
            "message": {"visited_urls_count": count},
        }
        logger.debug(f"✔ 获取已访问URL数量成功: {count}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✘  获取已访问URL数量失败: {e}")
        abort(500, description="✘  获取已访问URL数量失败")


@crawler_bp.route("/get_block_list", methods=["GET", "POST"])
def crawler_bp_get_block_list() -> Any:
    """获取屏蔽网址列表"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到获取屏蔽网址列表请求")
    try:
        block_list: list[str] = get_block_list()
        response_data = {
            "status": "success",
            "message": {"block_list": block_list},
        }
        logger.debug(f"✔ 获取屏蔽网址列表成功: {block_list}")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✘  获取屏蔽网址列表失败: {e}")
        abort(500, description="✘  获取屏蔽网址列表失败")
