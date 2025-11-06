"""注册表操作相关的功能"""

import winreg
import os


def add_to_startup(software_name, software_path=os.path.abspath(__file__)) -> bool:
    """将程序添加到开机启动项"""
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, software_name, 0, winreg.REG_SZ, software_path)
        winreg.CloseKey(reg_key)
        return True
    except WindowsError:
        return False


def remove_from_startup(software_name) -> bool:
    """将程序从开机启动项中移除"""
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(reg_key, software_name)
        winreg.CloseKey(reg_key)
        return True
    except WindowsError:
        return False


def is_in_startup(software_name) -> bool:
    """检查程序是否在开机启动项中"""
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(reg_key, software_name)
        winreg.CloseKey(reg_key)
        return True
    except WindowsError:
        return False
