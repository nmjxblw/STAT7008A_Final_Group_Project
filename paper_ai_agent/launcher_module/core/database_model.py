"""数据库模型模块"""

from ..__main__ import flask_database


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
        return f"<File id={self.file_id} title={self.title} author={self.author} publish_date={self.publish_date}>"
