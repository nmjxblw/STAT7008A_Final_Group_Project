import flask
from flask import Flask, config, Blueprint
from global_module import DATABASE_PATH
from pathlib import Path


class DefaultFlaskConfig(object):
    """默认的Flask配置类"""

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path.joinpath(Path.cwd(), DATABASE_PATH)}"
    """ 数据库连接URI """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ECHO = False


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
