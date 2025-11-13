from email import generator
import json
import sys
from typing import Any

from anyio import getnameinfo
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
from log_module import *  # 导入全局日志模块
from answer_generator_module import generator

generator_bp: Blueprint = Blueprint("generator_blueprint", __name__)
"""回答生成器蓝图模块"""


@generator_bp.route("/set_demand", methods=("POST",))
def set_demand() -> Any:
    """设置用户需求接口"""
    try:
        request_data: dict[str, Any] = request.get_json()
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求数据：{ request_data }")

        demand = request_data.get("demand", "")
        logger.debug(f"Received demand: {demand}")
        # 这里可以添加代码将需求传递给回答生成器模块
        if generator.set_demand(demand):
            response_data = {"status": "success", "message": "Demand set successfully"}
        else:
            response_data = {"status": "failure", "message": "Failed to set demand"}
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in set_demand: {e}")
        response_data = {"status": "error", "message": str(e)}
        return jsonify(response_data), 500
