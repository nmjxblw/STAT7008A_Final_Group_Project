import json
import flask
from flask import Blueprint, jsonify, render_template, abort, Response
from jinja2 import TemplateNotFound
from log_module import logger

test_bp: Blueprint = Blueprint("test_blueprint", __name__)
"""测试蓝图模块"""


@test_bp.route("/test/<input>", methods=("GET", "POST"))
def render_test_template(input: str) -> Response:
    """渲染测试模板"""
    obj = {"status": "success", "message": f"test_input:{input}"}
    try:
        logger.debug(f"object: {obj}")
        return jsonify(obj)
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        raise e
