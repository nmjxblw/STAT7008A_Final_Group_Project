"""创建系统托盘图标模块"""

import pystray
from pystray._base import Icon, MenuItem
from PIL import Image
from global_module import PROJECT_NAME, ICON_NAME
from pathlib import Path


def create_system_tray():
    """创建系统托盘图标"""
    image = Image.open(Path.cwd() / ICON_NAME)
    menu = pystray.Menu(pystray.MenuItem("退出", _on_exit))
    icon = pystray.Icon(PROJECT_NAME, image, "论文查询助手智能体", menu)

    import threading

    icon_thread = threading.Thread(target=lambda: icon.run(), args=())
    icon_thread.daemon = True  # 设置为守护线程，这样主程序退出时它会自动结束
    icon_thread.start()


def _on_exit(icon: Icon, item: MenuItem):
    """退出程序回调"""
    icon.stop()
    import signal

    signal.raise_signal(signal.SIGINT)
