"""托盘模块"""

from __future__ import annotations

__all__ = ["icon"]

from pystray._base import Icon


def _init():
    """初始化托盘图标功能"""
    global _has_create_system_tray
    if _has_create_system_tray:
        return
    else:
        from .create_tray import create_system_tray

        global icon
        icon = create_system_tray()
        _has_create_system_tray = icon is not None


_has_create_system_tray = False
"""是否存在创建系统托盘的功能标志位"""
icon: Icon
"""系统托盘图标实例"""

_init()
