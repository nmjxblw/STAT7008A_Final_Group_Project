import flask
from flask import Flask, config, Blueprint
from global_module import DATABASE_PATH
from pathlib import Path


class DefaultFlaskConfig(object):
    """默认的Flask配置类"""

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    """ 数据库连接URI """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """ 是否追踪对象修改 """
    SQLALCHEMY_RECORD_QUERIES = False
    """ 是否记录查询 """
    SQLALCHEMY_ECHO = False
    """ 如果设置成 True，SQLAlchemy 将会记录所有 发到标准输出(stderr)的语句 """
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": -1}
    """ SQLAlchemy引擎选项 """
    SQLALCHEMY_BINDS = {}
    """ SQLAlchemy数据库绑定 """
    SQLALCHEMY_MAX_OVERFLOW = 10
    """ 控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃。 """


class DevelopmentFlaskConfig(DefaultFlaskConfig):
    """开发环境的Flask配置类"""

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True


class DebugFlaskConfig(DefaultFlaskConfig):
    """调试环境的Flask配置类"""

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True
    TESTING = True


class ProductionFlaskConfig(DefaultFlaskConfig):
    """生产环境的Flask配置类"""

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ECHO = False
