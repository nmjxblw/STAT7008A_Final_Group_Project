import json
import os
from pathlib import Path
from typing import Any
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
import asyncio
import aiohttp  # 用于发起异步HTTP请求的库
import time
from ..database_model import File
from datetime import datetime
from log_module import *  # 导入全局日志模块

example_bp: Blueprint = Blueprint(
    "example_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""样例蓝图模块"""


@example_bp.route("/", methods=["GET", "POST"])
async def example_bp_main_page() -> Any:
    """样例主页接口"""
    try:
        logger.debug(f"渲染样例主页模板...")
        return render_template("example_main_page.html")
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        abort(500, description="渲染样例主页失败")
        raise e


@example_bp.route("/add_or_update_file", methods=["POST"])
async def example_bp_add_or_update_file() -> Any:
    """样例接口，添加或更新文件记录"""
    try:
        request_data: dict[str, Any] = request.get_json()
        logger.debug(f"样例接口请求数据: {request_data}")
        if request_data is None:
            logger.debug("请求数据解析异常...")
            return abort(400, description="请求数据解析异常，请检查请求格式")
        from ..database_operations import add_or_update_file_record

        if not asyncio.gather(add_or_update_file_record(request_data)):
            abort(500, description="添加或更新文件记录失败")

        response_data: dict[str, Any] = {
            "status": "success",
            "message": f"添加文件成功，文件ID为{{{request_data.get('file_id')}}}",
        }
        logger.debug(f"样例接口响应数据: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        # 后端数据插入异常，直接抛出异常
        abort(500, description="添加或更新文件记录失败")
        raise e


@example_bp.route("/<string:input_str>", methods=["GET", "POST"])
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
