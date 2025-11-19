from email import message
import glob
import json
from typing import Any
from crawler_module import crawler
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块
from file_classifier_module import (
    start_file_classify_task,
    pause_file_classify_task,
    stop_file_classify_task,
    resume_file_classify_task,
)
import sys
import threading

classifier_bp = Blueprint(
    "classifier_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""分类器蓝图模块"""


@classifier_bp.route("/file_classify_task", methods=["POST"])
def classifier_bp_file_classify_task() -> Any:
    """文件分类任务"""
    logger.debug(f"{sys._getframe().f_code.co_name}接口收到文件分类任务请求...")
    try:
        request_data: dict[str, Any] = request.get_json()
        if not isinstance(request_data, dict):
            abort(400, description="✖ 请求数据无效")
        message: str = request_data.get("message", "")
        message = message.lower()
        if message == "pause":
            # 暂停文件分类任务的逻辑
            pause_file_classify_task()
            response_data = {"status": "success", "message": "文件分类任务已暂停"}
        else:
            _thread = threading.Thread(target=start_file_classify_task, daemon=True)
            _thread.start()
            response_data = {"status": "success", "message": "文件分类任务正在执行"}
        return jsonify(response_data)
    except Exception as e:
        abort(500, description="✖ 启动文件分类任务失败")
        raise e
