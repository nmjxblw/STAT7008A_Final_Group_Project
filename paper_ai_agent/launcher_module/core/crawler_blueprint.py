from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

crawler_bp = Blueprint("crawler", __name__)
"""爬虫蓝图模块"""
