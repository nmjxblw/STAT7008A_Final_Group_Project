"""数据库模型模块"""

from utility_mode import SingletonMeta
from global_module import DATABASE_PATH
from pathlib import Path
import flask
from flask import Flask
from flask_sqlalchemy import (
    SQLAlchemy,
)
import log_module

logger = log_module.get_default_logger()
""" 全局日志记录器对象 """
