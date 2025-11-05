"""注册表模块"""

from __future__ import annotations  # 兼容未来版本的类型注解
import os

__all__ = [
    "add_to_startup",
    "remove_from_startup",
    "is_in_startup",
]


def add_to_startup():
    """添加到开机启动 (需要管理员权限)"""
    try:
        from .registry_api import add_to_startup as _add_to_startup

        return _add_to_startup(os.path.basename(__file__))
    except ImportError as e:
        raise e


def remove_from_startup():
    """从开机启动移除"""
    try:
        from .registry_api import (
            remove_from_startup as _remove_from_startup,
        )

        return _remove_from_startup(os.path.basename(__file__))
    except ImportError as e:
        raise e


def is_in_startup():
    """检查是否在开机启动中"""
    try:
        from .registry_api import is_in_startup as _is_in_startup

        return _is_in_startup(os.path.basename(__file__))
    except ImportError as e:
        raise e
