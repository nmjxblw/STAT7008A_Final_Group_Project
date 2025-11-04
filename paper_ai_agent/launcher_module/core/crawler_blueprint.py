from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import get_default_logger

logger = get_default_logger()
""" 全局日志记录器对象 """
crawler_bp = Blueprint(
    "crawler", __name__, template_folder=Path.joinpath(Path.cwd(), "frontend_module")
)
"""爬虫蓝图模块"""
