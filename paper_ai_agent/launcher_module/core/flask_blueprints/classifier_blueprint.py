import json
from typing import Any
from crawler_module import crawler
from flask import Blueprint, jsonify, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块

classifier_bp = Blueprint(
    "classifier_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""分类器蓝图模块"""
