"""
启动器核心模块

包含：
    1.Flask的蓝图模块
    2.数据库处理器
"""

from .main_logic import *
from .flask_blueprints import *

__all__ = [
    "crawler_bp",
    "example_bp",
    "generator_bp",
    "main_bp",
    "register_blueprints",
]
