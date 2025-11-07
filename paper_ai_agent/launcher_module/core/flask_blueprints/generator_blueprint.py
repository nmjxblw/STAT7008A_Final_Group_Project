from email import generator
import json
from typing import Any
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
from log_module import *  # 导入全局日志模块

generator_bp: Blueprint = Blueprint("generator_blueprint", __name__)
"""回答生成器蓝图模块"""


@generator_bp.route("/set_demand", methods=("POST",))
def set_demand() -> Any:
    """设置用户需求接口"""
    try:
        logger.debug(f"访问/set_demand接口...请求体为：{ request.get_data()}")
        request_data: dict[str, Any] = request.get_json()
        demand = request_data.get("demand", "")
        logger.debug(f"Received demand: {demand}")
        # 这里可以添加代码将需求传递给回答生成器模块
        response_data = {"status": "success", "message": "Demand set successfully"}
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in set_demand: {e}")
        response_data = {"status": "error", "message": str(e)}
        return jsonify(response_data), 500
