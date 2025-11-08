"""数据库操作模块"""

from datetime import date, datetime
import sys
from .database_model import File
from log_module import *  # 导入全局日志模块


async def query_files_by_attributes(filed_set: dict) -> list[File]:
    """
    根据指定属性查询文件记录

    参数：
        filed_set (dict): 包含查询属性的字典
    返回：
        files (list[File]): 符合条件的文件记录列表
    """
    try:
        logger.debug(f"正在根据属性查询文件记录，查询条件: {filed_set}")
        from ..__main__ import flask_database

        query = flask_database.session.query(File)
        for attr, value in filed_set.items():
            attr_name: str = attr.lower()
            if hasattr(File, attr_name):
                query = query.filter(getattr(File, attr_name) == value)
        files: list[File] = query.all()
        if not files:
            logger.debug("✖ 未找到符合条件的记录")
            return []
        else:
            logger.debug(f"✔ 查询成功，找到 {len(files)} 条记录")
            return files
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 查询文件记录失败: {e}")
        return []


async def add_or_update_file_to_database(file_data: object | dict) -> bool:
    """
    添加或更新文件记录到数据库

    参数：
        file_data (object): 文件对象，包含文件各字段信息
    返回：
        success (bool): 操作是否成功
    """
    try:
        logger.debug(f"{sys._getframe().f_code.co_name}接口被调用...")
        from ..__main__ import flask_database

        # 如果不是字典，使用File.from_object转换
        if not isinstance(file_data, dict):
            _temp_dict: dict = File.extract_to_file_dict(file_data)
        else:
            _temp_dict = file_data

        # 检查是否已有该文件记录
        existing_file: File | None = (
            flask_database.session.query(File)
            .filter_by(file_id=_temp_dict["file_id"])
            .first()
        )
        if existing_file is None:
            # 创建新记录
            new_file: File = File.from_dict(_temp_dict)
            flask_database.session.add(new_file)
            flask_database.session.commit()
            logger.debug(f"✔ 添加新文件记录，文件ID为{{{_temp_dict['file_id']}}}")
        else:
            existing_file.update_attributes_from_dict(_temp_dict)
            flask_database.session.commit()
            logger.debug(f"✔ 更新文件记录，文件ID为{{{_temp_dict['file_id']}}}")
        return True
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 添加或更新文件记录失败: {e}")
        return False
