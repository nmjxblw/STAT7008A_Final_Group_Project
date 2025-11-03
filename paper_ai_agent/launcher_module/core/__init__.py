"""
启动器核心模块
包含：1.Flask的蓝图模块
2.数据库处理器
"""

from .database_handler import *
from .crawler_blueprint import *
from .test_blueprint import *

__all__ = ["DBHandler", "crawler_bp", "test_bp"]
