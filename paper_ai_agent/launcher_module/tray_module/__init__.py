"""托盘模块"""

from __future__ import annotations
import os  # 兼容未来版本的类型注解

__all__ = ["create_system_tray"]


# 可选功能
def create_system_tray():
    """创建系统托盘"""
    try:
        from .create_tray import (
            create_system_tray as _create_system_tray,
        )

        return _create_system_tray()
    except ImportError as e:
        raise e
