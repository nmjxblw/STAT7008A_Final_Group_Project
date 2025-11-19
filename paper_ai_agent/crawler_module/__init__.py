"""爬虫模块"""

from __future__ import annotations
from typing import Any

__all__ = [
    "crawler",
    "start_crawling_task",
    "pause_crawling_task",
    "resume_crawling_task",
    "stop_crawling_task",
    "is_crawler_running",
    "update_crawler_config",
    "get_current_crawling_web",
    "get_current_crawling_article",
    "get_visited_urls_count",
    "get_block_list",
]

# 导出核心类
from .web_crawler import WebCrawler

crawler: WebCrawler = WebCrawler()
"""全局爬虫单例实例"""


def update_crawler_config(**kwargs) -> bool:
    """更新爬虫配置

    参数:
        **kwargs: 爬虫配置参数
    """
    return crawler.update_crawler_config(**kwargs)


def start_crawling_task() -> bool:
    """启动爬虫任务"""
    return crawler.start_crawling_task()


def pause_crawling_task() -> bool:
    """暂停爬虫任务"""
    return crawler.pause_crawling_task()


def resume_crawling_task() -> bool:
    """恢复爬虫任务"""
    return crawler.resume_crawling_task()


def stop_crawling_task() -> bool:
    """停止爬虫任务"""
    return crawler.stop_crawling_task()


def is_crawler_running() -> bool:
    """判断爬虫是否在运行"""
    return crawler.is_crawler_running()


def get_current_crawling_web() -> str:
    """获取当前爬虫网页"""
    return crawler.get_current_crawling_web()


def get_current_crawling_article() -> str:
    """获取当前爬虫文章标题"""
    return crawler.get_current_crawling_article()


def get_visited_urls_count() -> int:
    """获取已访问URL数量"""
    return crawler.get_visited_urls_count()


def get_block_list() -> list[str]:
    """获取屏蔽网址列表"""
    return crawler.get_block_list()
