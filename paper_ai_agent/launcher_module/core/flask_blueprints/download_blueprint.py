from concurrent.futures import thread
import json
from os import PathLike
from typing import Any

from prometheus_client import Summary
from global_module import blueprints
from log_module import *
from crawler_module import *
from flask import (
    Blueprint,
    jsonify,
    render_template,
    abort,
    request,
    send_file,
    send_from_directory,
)
from jinja2 import TemplateNotFound
from pathlib import Path

import sys
import threading
from global_module import SUMMARY_FILE
from database_module import export_files_to_csv

download_bp = Blueprint(
    "download_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""下载管理蓝图模块"""


@download_bp.route("/summary", methods=["GET", "POST"])
def download_bp_summary() -> Any:
    """下载管理主页接口"""
    logger.debug(f"{sys._getframe().f_code.co_name}接口请求下载总结csv...")
    try:
        file_path: str | PathLike = export_files_to_csv(SUMMARY_FILE)

        return send_from_directory(
            Path(file_path).parent, Path(file_path).name, as_attachment=True
        )
    except Exception as e:
        logger.debug(f"✖ 下载接口调用异常: {e}")
        abort(500, description="✖ 下载接口调用异常")
