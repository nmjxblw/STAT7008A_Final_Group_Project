"""爬虫模块"""

from __future__ import annotations  # 兼容未来版本的类型注解

# 延迟导入可选模块,避免缺少依赖时导入失败
__all__ = [
    "crawler",
]

# 导出核心类
import os
from .web_crawler import *

crawler: WebCrawler = WebCrawler()
""" 全局爬虫单例实例 """
