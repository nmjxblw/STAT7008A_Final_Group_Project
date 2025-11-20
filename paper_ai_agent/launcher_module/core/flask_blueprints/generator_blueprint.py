import sys
from typing import Any
from flask import Blueprint, jsonify, render_template, abort, Response, request
from jinja2 import TemplateNotFound
from log_module import *  # 导入全局日志模块
from answer_generator_module import generator
from database_module.operations import query_files_by_attributes

generator_bp: Blueprint = Blueprint("generator_blueprint", __name__)
"""回答生成器蓝图模块"""

_file_id_list: list[str] = []
""" 全局文件ID列表，存储最近查询的文件ID """
_reference_list: list[dict[str, Any]] = []
""" 全局引用列表，存储最近查询的文件记录 """


@generator_bp.route("/set_demand", methods=["POST"])
def set_demand() -> Any:
    """设置用户需求接口"""
    try:
        request_data: dict[str, Any] = request.get_json()
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求数据：{ request_data }")

        params: dict[str, Any] | None = request_data.get("params")
        if not isinstance(params, dict):
            abort(400, description="✖ 请求数据无效")
        question = params.get("question", "")
        if not isinstance(question, str) or question.strip() == "":
            abort(400, description="✖ 问题不能为空")
        _answer_type, _details = generator.set_demand(question)

        _reference_list.clear()
        _file_id_list.clear()
        for file_id, sim in _details[:5]:
            _query_files = query_files_by_attributes({"file_id": file_id})
            if isinstance(_query_files, list) and len(_query_files) > 0:
                file_records = _query_files[0]
                if isinstance(file_records, dict):
                    file_records["similarity"] = sim
                    _file_id_list.append(file_id)
                    _reference_list.append(file_records)

        response_data = {
            "status": "success",
            "message": {"answer_type": _answer_type, "details": _reference_list},
        }
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 设置用户需求失败: {e}")
        abort(500, description="✖ 设置用户需求失败")


@generator_bp.route("/get_LLM_reply", methods=["POST"])
def get_LLM_reply() -> Response:
    """获取LLM回复接口"""
    try:
        request_data: dict[str, Any] = request.get_json()
        logger.debug(f"{sys._getframe().f_code.co_name}接口请求数据：{ request_data }")
        message: str = request_data.get("message", "")
        _file_ids: list[str] = []
        if isinstance(message, dict):
            _file_ids = message.get("file_ids", [])
        if len(_file_ids) == 0:
            _file_ids = _file_id_list
        reply = generator.get_LLM_reply(reference=_file_ids)
        response_data = {"status": "success", "message": reply}
        return jsonify(response_data)
    except Exception as e:
        logger.debug(f"✖ 获取LLM回复失败: {e}")
        abort(500, description="✖ 获取LLM回复失败")
