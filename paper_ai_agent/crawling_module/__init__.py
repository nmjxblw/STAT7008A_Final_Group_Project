"""爬虫模块"""

# 延迟导入可选模块,避免缺少依赖时导入失败
__all__ = [
    "WebCrawler",
    "CrawlerWebAPIRouter",
    "TaskScheduler",
]

# 导出核心类
import os
from .web_crawler import *
from .crawler_web_api_router import *
from .scheduler import *


# 可选功能
def create_system_tray():
    """创建系统托盘 (需要安装 pystray)"""
    try:
        from .create_tray import create_system_tray as _create_system_tray

        return _create_system_tray()
    except ImportError:
        print("警告: pystray 未安装,系统托盘功能不可用")
        return None


def add_to_startup():
    """添加到开机启动 (需要管理员权限)"""
    try:
        from .registry_api import add_to_startup as _add_to_startup

        return _add_to_startup(os.path.basename(__file__))
    except ImportError:
        print("警告: 注册表API不可用")
        return False


def remove_from_startup():
    """从开机启动移除"""
    try:
        from .registry_api import remove_from_startup as _remove_from_startup

        return _remove_from_startup(os.path.basename(__file__))
    except ImportError:
        print("警告: 注册表API不可用")
        return False


def is_in_startup():
    """检查是否在开机启动中"""
    try:
        from .registry_api import is_in_startup as _is_in_startup

        return _is_in_startup(os.path.basename(__file__))
    except ImportError:
        print("警告: 注册表API不可用")
        return False
