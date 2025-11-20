"""数据库操作模块"""

from datetime import date, datetime
from os import PathLike
import sys
from typing import Any
import csv
import json
import pandas as pd
from sympy import im
from zipp import Path
from .models import File
from .core import session
from global_module import SUMMARY_FILE
from log_module import *  # 导入全局日志模块


def query_files_by_attributes(attributes: dict[str, Any]) -> list[dict[str, Any]]:
    """
    根据指定字段查询文件，以字典格式返回

    参数：
        attributes (dict): 包含查询属性的字典
    返回：
        files (list[dict[str, Any]]): 符合条件的文件记录列表
    """
    try:
        logger.debug(f"正在根据属性查询文件记录，查询条件: {attributes}")

        query = session.query(File)
        for attr, value in attributes.items():
            attr_name: str = attr.lower()
            if hasattr(File, attr_name):
                if attr_name == "keywords":
                    # 关键词使用模糊匹配
                    query = query.filter(
                        getattr(File, attr_name).ilike(f"%{str(value)}%")
                    )
                else:
                    query = query.filter(getattr(File, attr_name) == value)
        files_list: list[dict[str, Any]] = [f.to_dict() for f in query.all()]
        if not files_list:
            logger.debug("✖ 未找到符合条件的记录")
            return []
        else:
            logger.debug(f"✔ 查询成功，找到 {len(files_list)} 条记录")
            return files_list
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 查询文件记录失败: {e}")
        return []


def add_or_update_file_to_database(file_data: object | dict) -> bool:
    """
    添加或更新文件到数据库

    参数：
        file_data (object): 文件对象，包含文件各字段信息
    返回：
        success (bool): 操作是否成功
    """
    try:
        logger.debug(f"{sys._getframe().f_code.co_name}接口被调用...")

        # 如果不是字典，使用File.from_object转换
        if not isinstance(file_data, dict):
            _temp_dict: dict = File.extract_to_file_dict(file_data)
        else:
            _temp_dict = file_data

        # 检查是否已有该文件记录
        existing_file: File | None = (
            session.query(File).filter_by(file_id=_temp_dict["file_id"]).first()
        )
        if existing_file is None:
            # 创建新记录
            new_file: File = File.from_dict(_temp_dict)
            session.add(new_file)
            session.commit()
            logger.debug(f"✔ 添加新文件记录，文件ID为{{{_temp_dict['file_id']}}}")
        else:
            existing_file.update_attributes_from_dict(_temp_dict)
            session.commit()
            logger.debug(f"✔ 更新文件记录，文件ID为{{{_temp_dict['file_id']}}}")
        return True
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 添加或更新文件记录失败: {e}")
        return False


def get_all() -> list[dict[str, Any]]:
    """
    获取数据库中所有文件记录

    返回：
        files (list[dict[str, Any]]): 所有文件记录列表
    """
    try:
        logger.debug(f"{sys._getframe().f_code.co_name}接口被调用...")

        files_list: list[File] = session.query(File).all()
        result: list[dict[str, Any]] = [file.to_dict() for file in files_list]
        logger.debug(f"✔ 成功获取所有文件记录，共 {len(result)} 条记录")
        return result
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 获取所有文件记录失败: {e}")
        return []


def export_files_to_csv(csv_path: PathLike | str = SUMMARY_FILE) -> str | PathLike:
    """
    将数据库中的文件记录导出为CSV文件

    参数：
        csv_path (str|PathLike): 导出CSV文件的路径
    """
    try:
        logger.debug(f"{sys._getframe().f_code.co_name}接口被调用...")

        files_list: list[File] = session.query(File).all()
        if not files_list:
            logger.debug("✖ 数据库中没有文件记录可导出")
            return ""

        with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = [column.key for column in File.__table__.columns]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for file in files_list:
                writer.writerow(file.to_dict())
        logger.debug(f"✔ 成功将文件记录导出为CSV文件，路径为: {csv_path}")
        return csv_path
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 导出文件记录为CSV失败: {e}")
        return ""


def import_csv_to_database(csv_path: str) -> bool:
    """
    从CSV文件导入文件记录到数据库

    参数：
        csv_path (str): 导入CSV文件的路径
    返回：
        success (bool): 操作是否成功
    """
    try:
        logger.debug(f"{sys._getframe().f_code.co_name}接口被调用...")

        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            file_dict = row.to_dict()
            # 处理keywords字段，将字符串转换为列表
            if "keywords" in file_dict and isinstance(file_dict["keywords"], str):
                file_dict["keywords"] = json.loads(file_dict["keywords"])
            success = add_or_update_file_to_database(file_dict)
            if not success:
                logger.debug(
                    f"✖ 导入文件记录失败，文件ID为{{{file_dict.get('file_id', '未知')}}}"
                )
                return False
        logger.debug(f"✔ 成功从CSV文件导入文件记录，路径为: {csv_path}")
        return True
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 从CSV文件导入文件记录失败: {e}")
        return False
