from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块

crawler_bp = Blueprint(
    "crawler", __name__, template_folder=Path.joinpath(Path.cwd(), "frontend_module")
)
"""爬虫蓝图模块"""
