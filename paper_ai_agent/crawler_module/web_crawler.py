"""爬虫模块 - 网页爬虫类实现"""

import enum
import threading
from requests import Response
import requests
from bs4 import BeautifulSoup, PageElement, NavigableString, Tag
import urllib.robotparser
from urllib.parse import urljoin, urlparse
import time
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from global_module import crawler_config
from sympy import Basic
from utility_mode import SingletonMeta
from log_module import logger  # 导入全局日志模块


class State(enum.Enum):
    """爬虫状态枚举类"""

    IDLE = "IDLE"
    CRAWLING = "CRAWLING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class WebCrawler(metaclass=SingletonMeta):
    """网页爬虫类"""

    def __init__(self):
        self.session: requests.Session = requests.Session()
        """ 请求会话 """
        self.setup_session()
        self.visited_urls: set[str] = set()
        """ 已访问的URL集合 """
        self.respect_robots_txt: bool = True
        """ 是否遵守robots.txt协议 """
        self.current_crawling_web: str = ""
        """ 当前正在爬取的网页 """
        self.current_crawling_article: str = ""
        """ 当前正在爬取的文章 """
        self.total_files_downloaded: int = 0
        """ 已下载的文件总数 """
        self.crawling_log: list[dict] = []
        """ 爬取日志列表 """

        # 设置保存路径
        self.project_root: Path = Path.cwd()
        """ 项目根目录 """
        self.resource_path: Path = self.project_root / "Resource" / "Unclassified"
        """ 资源保存路径 """

        # 爬虫进度标识符
        self.task_progress: float = 0.0
        """ 爬虫任务进度 """
        self.current_state: State = State.IDLE
        """ 爬虫当前状态 """

        # 任务时间戳
        self.task_start_timestamp: datetime = datetime.now()
        """ 任务开始时间戳 """
        self.task_end_timestamp: datetime = datetime.now()
        """ 任务结束时间戳 """
        self.task_duration: timedelta = timedelta()
        """ 任务持续时间 """

        self.max_threads: int = os.cpu_count() or 4
        """ 最大线程数 """
        # 日志
        logger.debug(f"网页爬虫类实例化完成")

    def setup_session(self):
        """设置请求会话参数"""
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Connection": "keep-alive",
            }
        )

    def flush_runtime_cache_and_reset_state(self):
        """清除运行时临时缓存数据并重置状态"""
        self.current_crawling_web = ""
        self.current_crawling_article = ""
        self.crawling_log.clear()
        self.task_progress = 0.0
        self.current_state = State.IDLE
        logger.debug("✔ 爬虫运行时缓存数据已清除，状态已重置")

    def check_robots_txt(self, url: str) -> bool:
        """检查robots.txt协议"""
        if not self.respect_robots_txt:
            return True

        parsed = urlparse(url)
        """ 解析URL """
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        """ 构建基础URL """
        rp = urllib.robotparser.RobotFileParser()
        """ 创建机器人文件解析器 """
        rp.set_url(urljoin(base_url, "/robots.txt"))
        try:
            rp.read()
            return rp.can_fetch("*", url)
        except:
            return True

    def download_file(self, url: str, file_type: str) -> bytes | None:
        """下载特定类型文件"""
        if not self.check_robots_txt(url):
            return None

        try:
            response = self.session.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                # 文件内容类型验证
                content_type = response.headers.get("content-type", "")
                if self.validate_file_type(content_type, file_type):
                    return response.content
            return None
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return None

    def validate_file_type(self, content_type, expected_type):
        """验证文件类型匹配"""
        type_mapping = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".png": "image/png",
        }
        expected_mime = type_mapping.get(expected_type, "")
        return expected_mime in content_type

    def start_crawling_task(self) -> bool:
        """启动爬虫任务"""
        try:
            # 创建保存目录和日志目录
            self.resource_path.mkdir(parents=True, exist_ok=True)

            for website in crawler_config.crawling_source_list.to_list():
                self.current_crawling_web = website
                self.crawl_website(website)

            # 保存爬取日志
            self.save_crawling_log()
            return True
        except Exception as e:
            logger.debug(f"爬虫任务失败: {e}")
            return False
        finally:
            self.flush_runtime_cache_and_reset_state()

    def crawl_website(self, base_url: str):
        """爬取指定网站"""
        to_visit = [base_url]
        while to_visit:
            url = to_visit.pop(0)
            if url in self.visited_urls:
                continue

            # 检查是否在黑名单中
            if self.is_blocked_site(url):
                continue

            self.visited_urls.add(url)
            try:
                response: Response = self.session.get(
                    url, timeout=crawler_config.request_timeout
                )
                if response.status_code == 200:
                    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
                    self.extract_and_save_files(soup, url)
                    links: list[str] = self.extract_links(soup, base_url)
                    to_visit.extend(links)
                time.sleep(1)  # 请求延迟
            except Exception as e:
                print(f"访问失败 {url}: {e}")

    def is_blocked_site(self, url: str) -> bool:
        """检查URL是否在黑名单中"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        for blocked in crawler_config.blocked_sites:
            if blocked in domain or blocked in url:
                return True
        return False

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """从页面提取链接"""
        links: list[str] = []
        for link in soup.find_all("a", href=True):
            if link is None:
                continue
            if isinstance(link, Tag):
                href = str(link.get("href", ""))
                if href == "":
                    continue
                full_url = urljoin(base_url, href)

                # 只爬取同域名下的链接
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.append(full_url)
        return links

    def extract_and_save_files(self, soup: BeautifulSoup, page_url: str):
        """提取并保存文件"""
        # 查找所有可能的文件链接
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            if link is None:
                continue
            if isinstance(link, Tag):
                href = str(link.get("href", ""))
                if href == "":
                    continue
                full_url = urljoin(page_url, href)

                # 检查文件类型
                for file_type in crawler_config.file_type:
                    if full_url.lower().endswith(file_type):
                        # 检查关键词
                        if self.match_keywords(link.text, soup):
                            self.current_crawling_article = (
                                link.text or os.path.basename(urlparse(full_url).path)
                            )
                            self.download_and_save_file(full_url, file_type)

    def match_keywords(self, text: str, soup: BeautifulSoup) -> bool:
        """匹配关键词"""
        if not crawler_config.crawling_keywords:
            return True  # 如果没有设置关键词,则匹配所有

        # 获取链接文本和周围文本
        search_text = text + " " + soup.get_text()

        for keyword in crawler_config.crawling_keywords.to_list():
            if re.search(keyword, search_text, re.IGNORECASE):
                return True
        return False

    def download_and_save_file(self, url: str, file_type: str):
        """下载并保存文件"""
        try:
            file_content = self.download_file(url, file_type)
            if file_content:
                self.save_file(file_content, url, file_type)
        except Exception as e:
            print(f"下载和保存文件失败 {url}: {e}")

    def save_file(self, content: bytes, url: str, file_type: str):
        """保存文件到指定目录"""
        try:
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            # 创建按类型和时间分类的目录
            file_type_name = file_type.upper().replace(".", "")
            save_dir = self.resource_path / file_type_name / timestamp
            save_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            filename = os.path.basename(urlparse(url).path)
            if not filename or filename == "":
                filename = f"file_{self.total_files_downloaded}{file_type}"

            file_path = save_dir / filename

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(content)

            self.total_files_downloaded += 1

            # 记录到日志
            logger.debug(f"✔ 保存文件:{file_path}\tURL:{url}")

        except Exception as e:
            logger.debug(f"✘ 保存文件失败 {url}: {e}")
            raise e

    def save_crawling_log(self):
        """保存爬取日志"""
        try:
            for entry in self.crawling_log:
                log_line = f"[{entry['timestamp']}] FileName:\"{entry['filename']}\" Url:\"{entry['url']}\"\n"
                logger.info(log_line.strip())
        except Exception as e:
            raise e  # 抛出异常，让日志来定位报错

    # API接口方法
    def get_current_crawling_web(self) -> str:
        """获取当前正在爬取的网页"""
        return self.current_crawling_web

    def get_current_crawling_article(self) -> str:
        """获取当前正在爬取的文章"""
        return self.current_crawling_article

    def get_crawling_task_progress(self) -> float:
        """获取爬取工作进度"""
        if not crawler_config.crawling_source_list:
            return 0.0
        # 简单的进度计算: 已访问URL数 / 预估总URL数
        # 这是一个简化的实现
        return min(
            100.0,
            (
                len(self.visited_urls)
                / max(1, len(crawler_config.crawling_source_list) * 10)
            )
            * 100,
        )

    def get_block_list(self) -> list[str]:
        """获取当前的黑名单列表"""
        if isinstance(crawler_config.blocked_sites.to_list(), list):
            return crawler_config.blocked_sites.to_list()
        return []
