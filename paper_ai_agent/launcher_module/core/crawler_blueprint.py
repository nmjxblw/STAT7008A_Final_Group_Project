from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

crawler_bp = Blueprint(
    "crawler", __name__, template_folder=r"paper_ai_agent/front_end_module"
)
"""爬虫蓝图模块"""
