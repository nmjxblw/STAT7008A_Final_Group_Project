from ...__main__ import launcher_app
import json
from typing import Any
import flask
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
from pathlib import Path
from log_module import *  # 导入全局日志模块


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
        logger.debug("跳转到主页...")
        return render_template("index.html")
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        raise e


# 处理500内部服务器错误，通常返回JSON
@launcher_app.errorhandler(500)
def internal_server_error(error: Exception) -> tuple[Response, int]:
    # 记录错误日志到服务器控制台，便于调试
    launcher_app.logger.error(f"后端处理异常: {error}")
    # 返回JSON格式的错误信息
    return (
        jsonify(
            {
                "status": "error",
                "message": "后端处理异常。操作未成功完成。",
                "error": str(error),
                "error_code": 500,
            }
        ),
        500,
    )


@launcher_app.errorhandler(405)
def method_not_allowed(error: Exception) -> tuple[Response, int]:
    # 记录错误日志到服务器控制台，便于调试
    logger.error(f"方法不允许: {error}")
    # 尝试从异常中获取允许的方法列表；如果不可用则使用空列表
    try:
        valid_methods = getattr(error, "valid_methods", None) or []
        # 确保都是字符串
        valid_methods = [str(m) for m in valid_methods]
    except Exception:
        valid_methods = []

    # 实际接收到的请求方法优先使用 flask.request.method，避免依赖异常对象的属性
    try:
        received_method = request.method
    except Exception:
        received_method = None

    allowed_text = ", ".join(valid_methods) if valid_methods else ""
    message = (
        f"收到的请求方法为{received_method}，仅接受方法[{allowed_text}]"
        if received_method
        else f"仅接受方法[{allowed_text}]"
    )

    # 返回JSON格式的错误信息
    return (
        jsonify(
            {
                "status": "error",
                "message": message,
                "error": str(error),
                "error_code": 405,
                "allowed_methods": valid_methods,
            }
        ),
        405,
    )
