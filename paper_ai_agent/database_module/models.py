"""数据库模型定义模块"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date

# 定义基类
_Base = declarative_base()
""" 数据库模型基类 """


class File(_Base):
    """文件数据库模型数据结构，表示存储在数据库中的文件信息"""

    __tablename__ = "file"
    """ 数据库表名称 """

    # region 数据库字段定义
    file_id = Column(String(50), primary_key=True)
    """ 文件ID """
    title = Column(String(256), nullable=True)
    """ 文件标题 """
    summary = Column(Text, nullable=True)
    """ 文件摘要 """
    content = Column(Text, nullable=True)
    """ 文件内容 """
    keywords = Column(Text, nullable=True)  # "keywords|name"
    """ 文件关键词 """
    author = Column(String(50), nullable=True)
    """ 文件作者 """
    text_length = Column(Integer, nullable=True)
    """ 文件文本长度 """
    file_name = Column(String(256), nullable=True)
    """ 文件名 """

    # endregion

    def __repr__(self) -> str:
        """返回文件字典表示的字符串形式"""
        return str(self.to_dict())

    def to_dict(self) -> dict:
        """将文件对象转换为字典表示"""
        _dict = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue

            if "date" in key and isinstance(value, (datetime, date)):
                # 转换日期时间为ISO格式字符串
                _dict[key] = value.isoformat()
            elif "keywords" == key and isinstance(value, str):
                _dict[key] = value.split(r"[,|]+") if value else []
            else:
                _dict[key] = value
        return _dict

    def update_attributes_from_dict(self, data: dict) -> None:
        """从字典更新文件对象的属性"""
        for key, value in data.items():
            if hasattr(self, key):
                if "date" in key and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                elif "keywords" == key and isinstance(value, list):
                    value = "|".join(value)
                setattr(self, key, value)

    @classmethod
    def from_object(cls, obj: object) -> "File":
        """从对象创建文件实例"""
        return cls.from_dict(obj.__dict__)

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        """从字典创建文件实例"""
        if data.get("file_id") == "":
            raise ValueError("字典缺少file_id键，无法创建File实例")
        file_instance = cls()
        file_instance.update_attributes_from_dict(data)
        return file_instance

    @classmethod
    def extract_to_file_dict(cls, obj: object) -> dict:
        """从对象提取文件信息为字典表示"""
        file_instance = cls.from_object(obj)
        return file_instance.to_dict()
