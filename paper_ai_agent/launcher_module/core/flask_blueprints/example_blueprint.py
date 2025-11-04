import json
from pathlib import Path
from typing import Any
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
from ..__main__ import _database, File
import log_module

logger = log_module.get_default_logger()
""" 全局日志记录器对象 """

example_bp: Blueprint = Blueprint(
    "example_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""样例蓝图模块"""


@example_bp.route("/<string:input_str>", methods=("GET", "POST"))
def example_bp_webapi_example(input_str: str) -> Response:
    """样例接口，返回输入字符串"""
    response_data = {"status": "success", "message": f"input:{input_str}"}
    try:
        logger.debug(f"样例接口响应数据: {response_data}")
        return jsonify(response_data)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        raise e


@example_bp.route("/<string:file_id>", methods=("GET", "POST"))
def example_bp_webapi_file(file_id: str) -> Any:
    """样例接口，返回文件ID"""
    response_data = {"status": "success", "message": f"file_id:{file_id}"}
    try:
        logger.debug(f"样例接口响应数据: {response_data}")
        new_file: File = File(file_id=file_id)
        _database.session.add(new_file)
        _database.session.commit()
        return jsonify(response_data)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        raise e


@example_bp.route("/", methods=("GET", "POST"))
def example_bp_main_page() -> Any:
    """样例主页接口"""
    try:
        logger.debug(f"渲染样例主页模板...")
        return render_template("example_main_page.html")
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        raise e
