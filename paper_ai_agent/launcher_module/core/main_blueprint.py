import json
from typing import Any
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
from pathlib import Path
import log_module

logger = log_module.get_default_logger()
""" 全局日志记录器对象 """

main_bp: Blueprint = Blueprint(
    "main_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""主页蓝图模块"""


@main_bp.route("/", methods=("GET", "POST"))
def render_main_template() -> Any:
    """渲染主页模板"""
    try:
        logger.debug("渲染主页模板...")
        return render_template("index.html")
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        raise e
