"""创建系统托盘图标模块"""

import pystray
from pystray._base import Icon, MenuItem
from PIL import Image
from global_module import PROJECT_NAME, ICON_NAME
from pathlib import Path


def create_system_tray() -> Icon:
    """创建系统托盘图标"""
    from log_module import logger  # 避免循环导入

    logger.debug("正在创建系统托盘图标...")
    image = Image.open(Path.cwd() / ICON_NAME)
    menu = pystray.Menu(pystray.MenuItem("exit", _on_exit))
    icon = pystray.Icon(PROJECT_NAME, image, "Paper AI Agent", menu)
    logger.debug("系统托盘图标创建完成，正在启动托盘线程...")
    import threading

    icon_thread = threading.Thread(target=lambda: icon.run(), args=())
    icon_thread.daemon = True  # 设置为守护线程，这样主程序退出时它会自动结束
    icon_thread.start()
    logger.debug("系统托盘图标线程已启动。")

    return icon


def _on_exit(icon: Icon, item: MenuItem):
    """退出程序回调"""
    icon.stop()
    from log_module import logger  # 避免循环导入
    import signal

    logger.debug("系统托盘退出选项被点击，正在关闭程序...")
    signal.raise_signal(signal.SIGINT)
