from crawler_module import crawler
from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块

crawler_bp = Blueprint(
    "crawler_blueprint",
    __name__,
    template_folder=Path.joinpath(Path.cwd(), "frontend_module"),
)
"""爬虫蓝图模块"""


@crawler_bp.route("/crawler/start_crawling_task", methods=["GET"])
def start_crawling_task():
    """启动爬虫任务"""
    logger.debug("收到启动爬虫任务请求")
    try:
        crawler.start_crawling_task()
    except Exception as e:
        abort(500, description="启动爬虫任务失败")
        raise e
    return render_template("crawler/start_crawling_task.html")
