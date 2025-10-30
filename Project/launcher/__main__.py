"""启动模块"""

import os
from pathlib import Path
import pathlib
import flask
import threading
import json
from global_mode.global_dict import globals  # 导入全局变量模块

app_settings_file_name = Path.joinpath(Path.cwd(), "app_settings.json")
"""应用设置文件名"""

launcher_app = flask.Flask("launcher_app")
"""flask应用实例"""


def main():
    """程序入口函数"""
    try:
        globals["app_config"] = json.load(
            open(app_settings_file_name, "r", encoding="utf-8")
        )
        print(f"应用设置加载成功: {globals['app_config']['crawling_mode_config']}")
    except Exception as e:
        print(f"加载应用设置时发生错误: {e}")
    # launcher_app.run(debug=True)


if __name__ == "__main__":
    main()
