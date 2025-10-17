"""爬虫模块"""

from .create_tray import create_system_tray
from .add_to_startup import *

__all__ = [
    "create_system_tray",
    "remove_from_startup",
    "add_to_startup",
    "is_in_startup",
]
