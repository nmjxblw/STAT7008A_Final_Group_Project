from concurrent.futures import thread
import json
from typing import Any
from global_module import blueprints
from log_module import *
from crawler_module import *
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from database_module.operations import export_files_to_csv
import sys
import threading

database_bp = Blueprint(
    "database_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""数据库管理蓝图模块"""


@database_bp.route("/get_all_files", methods=["GET", "POST"])
def database_bp_get_all_files() -> Any:
    """获取数据库中所有文件记录"""
    logger.debug(f"{sys._getframe().f_code.co_name}接口收到获取所有文件记录请求...")
    try:
        from database_module import get_all

        all_files = get_all()
        response_data = {"status": "success", "message": all_files}
        return jsonify(response_data)
    except Exception as e:
        abort(500, description="✖ 获取文件记录失败")
        raise e


@database_bp.route("/to_csv", methods=["GET", "POST"])
def database_bp_export_to_csv() -> Any:
    """将数据库中的文件记录导出为CSV文件"""
    logger.debug(f"{sys._getframe().f_code.co_name}接口收到导出CSV请求...")
    try:

        csv_path = export_files_to_csv()
        response_data = {"status": "success", "message": f"文件已导出到 {csv_path}"}
        return jsonify(response_data)
    except Exception as e:
        abort(500, description="✖ 导出CSV文件失败")
        raise e
