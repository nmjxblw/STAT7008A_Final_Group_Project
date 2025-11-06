"""数据库操作模块"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from ..__main__ import flask_database
from .database_model import File
from log_module import *  # 导入全局日志模块


async def add_or_update_file_record(file_data: dict) -> bool:
    """
    添加或更新文件记录到数据库

    参数：
        file_data (dict): 文件数据字典，包含文件各字段信息
    返回：
        success (bool): 操作是否成功
    """
    try:
        logger.debug(f"正在添加或更新文件记录，文件ID: {file_data.get('file_id')}")
        file_id: str | None = file_data.get("file_id")
        if not file_id:
            logger.debug("✖ 文件数据缺少file_id，无法添加或更新记录")
            return False

        existing_file: File | None = flask_database.session.get(File, file_id)
        if existing_file:
            # 更新已有记录
            for attr, value in file_data.items():
                attr_name: str = attr.lower()
                if hasattr(existing_file, attr_name):
                    if "date" in attr_name:
                        value = datetime.fromisoformat(value)
                    setattr(existing_file, attr_name, value)
            flask_database.session.commit()
            logger.debug(f"✔ 文件记录更新成功，文件ID: {file_id}")
        else:
            # 添加新记录
            new_file = File()
            for attr, value in file_data.items():
                attr_name = attr.lower()
                if hasattr(new_file, attr_name):
                    setattr(new_file, attr_name, value)
            flask_database.session.add(new_file)
            flask_database.session.commit()
            logger.debug(f"✔ 文件记录添加成功，文件ID: {file_id}")
        return True
    except Exception as e:
        # 处理异常情况，记录日志等
        logger.debug(f"✖ 添加或更新文件记录失败: {e}")
        return False
