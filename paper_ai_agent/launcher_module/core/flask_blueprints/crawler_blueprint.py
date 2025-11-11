import json
from typing import Any
from crawler_module import crawler  # 在模块导入时实例化全局爬虫类，单例模式
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块
import sys

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
        config_data = request.get_json()
        logger.debug(f"爬虫配置请求数据: {config_data}")
        response_data = {"status": "success", "message": "爬虫配置已更新"}
        logger.debug("✔ 爬虫配置更新成功")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 爬虫配置更新失败: {e}")
        abort(500, description="✖ 设置爬虫配置失败")


@crawler_bp.route("/start_crawling_task", methods=["GET", "POST"])
def crawler_bp_start_crawling_task() -> Any:
    """启动爬虫任务"""
    logger.debug(f"{sys._getframe().f_code.co_name}收到启动爬虫任务请求")
    try:
        if crawler.start_crawling_task():
            response_data = {"status": "success", "message": "爬虫任务已执行完毕"}
            logger.debug("✔ 爬虫任务执行成功")
        else:
            response_data = {"status": "error", "message": "爬虫任务执行失败"}
            logger.debug("✖ 爬虫任务执行失败")
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
