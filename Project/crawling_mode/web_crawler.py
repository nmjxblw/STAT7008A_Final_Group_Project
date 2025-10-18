import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urljoin, urlparse
import time
import os
from .crawling_config import CrawlingConfig


class WebCrawler:
    """网页爬虫类"""

    def __init__(self, crawling_config: CrawlingConfig):
        self.config = crawling_config
        self.session = requests.Session()
        self.setup_session()
        self.visited_urls = set()
        self.respect_robots_txt = True
        self.current_crawling_web = ""
        self.current_crawling_article = ""

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

    def check_robots_txt(self, url: str) -> bool:
        """检查robots.txt协议"""
        if not self.respect_robots_txt:
            return True

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        rp = urllib.robotparser.RobotFileParser()
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
    
    @
