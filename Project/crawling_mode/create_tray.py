import pystray
from PIL import Image
import threading


def create_system_tray():
    """创建系统托盘图标"""
    image = Image.new("RGB", (64, 64), "white")
    menu = pystray.Menu(
        pystray.MenuItem("显示窗口", show_window), pystray.MenuItem("退出", exit_app)
    )
    icon = pystray.Icon("daily_crawling", image, "爬虫模块", menu)
    icon.run()
