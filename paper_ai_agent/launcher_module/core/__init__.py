"""
启动器核心模块
包含：1.Flask的蓝图模块
2.数据库处理器
"""

from .database_model import *
from .crawler_blueprint import *
from .example_blueprint import *

__all__ = ["crawler_bp", "example_bp"]
