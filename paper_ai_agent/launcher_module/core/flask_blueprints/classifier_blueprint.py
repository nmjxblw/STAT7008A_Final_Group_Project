import json
from typing import Any
from crawler_module import crawler
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块
from file_classifier_module import start_file_classify_task
import sys

classifier_bp = Blueprint(
    "classifier_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""分类器蓝图模块"""


@classifier_bp.route("/start_file_classify_task", methods=["POST"])
def classifier_bp_start_file_classify_task() -> Any:
    """启动文件分类任务"""
    logger.debug(f"{sys._getframe().f_code.co_name}接口收到启动文件分类任务请求...")
    try:
        request_data: dict = request.get_json()
        if start_file_classify_task(**request_data):
            response_data = {"status": "success", "message": "文件分类任务已执行完毕"}
            logger.debug("✔ 文件分类任务执行成功")
        else:
            response_data = {"status": "error", "message": "文件分类任务执行失败"}
            logger.debug("✖ 文件分类任务执行失败")
        return jsonify(response_data)
    except Exception as e:
        abort(500, description="✖ 启动文件分类任务失败")
        raise e
