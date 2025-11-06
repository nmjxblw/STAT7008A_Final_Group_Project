import sys
import pystray
from PIL import Image


def create_system_tray():
    """创建系统托盘图标"""
    image = Image.new("RGB", (64, 64), "white")
    menu = pystray.Menu(pystray.MenuItem("退出", sys.exit()))
    icon = pystray.Icon("daily_crawling", image, "爬虫模块", menu)
    icon.run()
