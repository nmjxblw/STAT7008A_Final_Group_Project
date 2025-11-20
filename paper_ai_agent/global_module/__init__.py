"""全局变量模块"""

from json import load
import os
from dotenv import load_dotenv
from .global_dynamic_object import *

__all__ = [
    "GlobalDynamicObject",
    "globals",
    "PROJECT_NAME",
    "PROJECT_DESCRIPTION",
    "PROJECT_AUTHOR",
    "DATABASE_PATH",
    "HOST",
    "PORT",
    "API_KEY",
    "USING_PROXY",
    "AUTO_CRAWL",
    "crawler_config",
    "answer_generator_config",
    "file_classifier_config",
]
assert load_dotenv(
    encoding="utf-8", verbose=True
), f".env文件加载失败, 请确保.env文件路径在[{os.getcwd()}]下"  # 从.env文件加载环境变量
# region 项目静态信息
PROJECT_NAME: str = os.getenv("PROJECT_NAME", "")
"""项目名称"""
PROJECT_DESCRIPTION: str = os.getenv("PROJECT_DESCRIPTION", "")
"""项目描述"""
PROJECT_AUTHOR: str = os.getenv("PROJECT_AUTHOR", "")
"""项目作者"""
DATABASE_PATH: Path = Path.joinpath(Path.cwd(), os.getenv("DATABASE_PATH", ""))
"""数据库路径"""
HOST: str = os.getenv("HOST", "0.0.0.0")
"""主机名"""
PORT: int = int(os.getenv("PORT", 8080))
"""端口号"""
assert os.getenv("API_KEY"), "API_KEY环境变量未设置，请在.env文件中配置"
API_KEY: str = os.getenv("API_KEY", "")
"""API密钥"""
if len(API_KEY) <= 0:
    raise ValueError("API_KEY环境变量未设置，请在.env文件中配置")
USING_PROXY: bool = os.getenv("USING_PROXY", "").lower() in ("1", "true", "yes")
"""是否使用代理"""
AUTO_CRAWL: bool = os.getenv("AUTO_CRAWL", "").lower() in ("1", "true", "yes")
"""是否自动爬取"""
ICON_NAME: str = os.getenv("ICON_NAME", "app.ico")
"""图标文件名"""
RESOURCE_DIR: Path = Path.joinpath(Path.cwd(), os.getenv("RESOURCE_DIR", "Resource"))
"""PDF存放资源目录"""
CLASSIFIED_DIR: Path = Path.joinpath(
    RESOURCE_DIR, os.getenv("CLASSIFIED_DIR", "Classified")
)
"""已分类文件目录"""
UNCLASSIFIED_DIR: Path = Path.joinpath(
    RESOURCE_DIR, os.getenv("UNCLASSIFIED_DIR", "Unclassified")
)
"""未分类文件目录"""
SUMMARY_FILE: Path = Path.joinpath(
    RESOURCE_DIR, os.getenv("SUMMARY_FILE", "summary.csv")
)
"""总结文件名"""
# endregion
