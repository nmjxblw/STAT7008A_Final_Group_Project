import json
import os
from pathlib import Path
import re
import sys
from typing import Any
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
import asyncio
import aiohttp  # 用于发起异步HTTP请求的库
import time
from datetime import datetime
from log_module import *  # 导入全局日志模块
from database_module import (
    File,
    query_files_by_attributes,
    add_or_update_file_to_database,
)

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
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求渲染样例主页...")
        return render_template("example_main_page.html")
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        logger.debug(f"✖ 渲染样例主页失败: {e}")
        abort(500, description="✖ 渲染样例主页失败")


@example_bp.route("/add_or_update_file", methods=["POST"])
def example_bp_add_or_update_file() -> Any:
    """样例接口，添加或更新文件记录"""
    try:
        request_data: dict[str, Any] = request.get_json()
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求数据: {request_data}")
        if request_data is None:
            logger.debug("请求数据解析异常...")
            return abort(400, description="✖ 请求数据解析异常，请检查请求格式")

        # 执行添加或更新文件记录操作，异步等待结果
        if not add_or_update_file_to_database(request_data):
            abort(500, description="✖ 添加或更新文件记录失败")

        response_data: dict[str, Any] = {
            "status": "success",
            "message": f"添加文件成功，文件ID为{{{request_data.get('file_id')}}}",
        }
        logger.debug(f"{sys._getframe().f_code.co_name}接口响应数据: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        # 后端数据插入异常，直接抛出异常
        logger.debug(f"✖ 添加或更新文件记录失败: {e}")
        abort(500, description="✖ 添加或更新文件记录失败")


@example_bp.route("/query_files_by_attributes", methods=["POST"])
async def example_bp_query_files_by_attributes() -> Any:
    """样例接口，根据属性查询文件记录"""
    try:
        request_data: dict[str, Any] = request.get_json()
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求数据: {request_data}")
        if request_data is None:
            logger.debug("✖ 请求数据解析异常")
            return abort(400, description="✖ 请求数据解析异常，请检查请求格式")

        # 提取查询属性
        query_attributes: dict = {}
        for attr, value in request_data.items():
            attr_name: str = attr.lower()
            if hasattr(File, attr_name):
                if "date" in attr_name and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                query_attributes[attr_name] = value
        # 执行查询，异步获取结果
        files = query_files_by_attributes(query_attributes)
        response_data = {
            "status": "success",
            "message": files,
        }
        logger.debug(f"{sys._getframe().f_code.co_name}接口响应数据: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        # 后端查询异常，直接抛出异常
        logger.debug(f"✖ 查询文件记录失败: {e}")
        abort(500, description="✖ 查询文件记录失败")


@example_bp.route("/<string:input_str>", methods=["GET"])
def example_bp_webapi_example(input_str: str) -> Response:
    """样例接口，返回输入字符串"""

    try:
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求数据: {input_str}")
        response_data = {"status": "success", "message": f"input:{input_str}"}
        logger.debug(f"{sys._getframe().f_code.co_name}接口响应数据: {response_data}")
        return jsonify(response_data)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        logger.debug(f"✖ 处理输入字符串失败: {e}")
        abort(500, description="✖ 处理输入字符串失败")
