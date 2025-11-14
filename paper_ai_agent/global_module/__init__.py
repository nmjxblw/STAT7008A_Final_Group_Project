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
    "crawler_config",
    "answer_generator_config",
    "file_classifier_config",
]
load_dotenv(encoding="utf-8", verbose=True)  # 从.env文件加载环境变量
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
API_KEY: str = os.getenv("API_KEY", "")
"""API密钥"""
USING_PROXY: bool = os.getenv("USING_PROXY", "").lower() in ("1", "true", "yes")
"""是否使用代理"""
# endregion
