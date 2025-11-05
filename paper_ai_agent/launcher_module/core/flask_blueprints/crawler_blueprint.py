import json
from typing import Any
from crawler_module import crawler
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块

crawler_bp = Blueprint(
    "crawler_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""爬虫蓝图模块"""


@crawler_bp.route("/setup_crawler_config", methods=["POST"])
def crawler_bp_setup_crawler_config():
    """设置爬虫配置"""
    logger.debug("收到设置爬虫配置请求")
    try:
        config_data = request.get_json()
        logger.debug(f"爬虫配置请求数据: {config_data}")
        response_data = {"status": "success", "message": "爬虫配置已更新"}
        logger.debug("✔ 爬虫配置更新成功")
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 爬虫配置更新失败: {e}")
        abort(500, description="设置爬虫配置失败")


@crawler_bp.route("/start_crawling_task", methods=["GET"])
def crawler_bp_start_crawling_task() -> Any:
    """启动爬虫任务"""
    logger.debug("收到启动爬虫任务请求")
    try:
        if crawler.start_crawling_task():
            response_data = {"status": "success", "message": "爬虫任务已执行完毕"}
            logger.debug("✔ 爬虫任务执行成功")
        else:
            response_data = {"status": "error", "message": "爬虫任务执行失败"}
            logger.debug("✖ 爬虫任务执行失败")
        return jsonify(response_data)
    except Exception as e:
        abort(500, description="启动爬虫任务失败")
        raise e
