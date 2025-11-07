"""数据库模型模块"""

from ..__main__ import flask_database
from datetime import datetime, date


class File(flask_database.Model):
    """文件模型类，表示存储在数据库中的文件信息"""

    __tablename__ = "file"
    """ 数据库表名称 """

    # region 数据库字段定义
    file_id = flask_database.Column(flask_database.String(50), primary_key=True)
    """ 文件ID """
    title = flask_database.Column(flask_database.String(256), nullable=True)
    """ 文件标题 """
    summary = flask_database.Column(flask_database.Text, nullable=True)
    """ 文件摘要 """
    content = flask_database.Column(flask_database.Text, nullable=True)
    """ 文件内容 """
    keywords = flask_database.Column(flask_database.Text, nullable=True)
    """ 文件关键词 """
    author = flask_database.Column(flask_database.String(50), nullable=True)
    """ 文件作者 """
    publish_date = flask_database.Column(flask_database.DateTime, nullable=True)
    """ 文件发布日期 """
    download_date = flask_database.Column(flask_database.DateTime, nullable=True)
    """ 文件下载日期 """
    total_tokens = flask_database.Column(flask_database.Integer, nullable=True)
    """ 文件总令牌数 """
    unique_tokens = flask_database.Column(flask_database.Integer, nullable=True)
    """ 文件唯一令牌数 """
    text_length = flask_database.Column(flask_database.Integer, nullable=True)
    """ 文件文本长度 """

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
            else:
                _dict[key] = value
        return _dict

    def update_attributes_from_dict(self, data: dict) -> None:
        """从字典更新文件对象的属性"""
        for key, value in data.items():
            if hasattr(self, key):
                if "date" in key and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                    # 不处理报错，让exception handler捕获
                setattr(self, key, value)

    @classmethod
    def from_object(cls, obj: object) -> "File":
        """从对象创建文件实例"""
        return cls.from_dict(obj.__dict__)

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        """从字典创建文件实例"""
        file_instance = cls()
        for key, value in data.items():
            if hasattr(file_instance, key):
                if "date" in key and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                    # 不处理报错，让exception handler捕获
                setattr(file_instance, key, value)
        if not file_instance.file_id:
            raise ValueError("字典缺少file_id键，无法创建File实例")
        return file_instance

    @classmethod
    def extract_to_file_dict(cls, obj: object) -> dict:
        """从对象提取文件信息为字典表示"""
        file_instance = cls.from_object(obj)
        return file_instance.to_dict()
