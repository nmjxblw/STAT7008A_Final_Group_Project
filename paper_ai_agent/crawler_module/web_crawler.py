"""爬虫模块 - 网页爬虫类实现"""

import enum
import random
import threading
from requests import Response
import requests
from bs4 import BeautifulSoup, PageElement, NavigableString, Tag
import urllib.robotparser
from urllib.parse import ParseResult, ParseResultBytes, urljoin, urlparse
import time
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from global_module import crawler_config
from sympy import Basic
from utility_module import SingletonMeta
from log_module import logger  # 导入全局日志模块


class State(enum.Enum):
    """爬虫状态枚举类"""

    IDLE = "IDLE"
    CRAWLING = "CRAWLING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


_my_headers: list[str] = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
    "Opera/9.25 (Windows NT 5.1; U; en)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12",
    "Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
]
"""爬虫请求头列表"""


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
        # robots.txt 解析器缓存: netloc -> RobotFileParser
        self._robots_parsers = {}
        # site-specific rules cache: netloc -> {crawl_delay: float|None, disallow_all: bool}
        self._site_rules = {}

        # 代理相关配置
        self.use_proxy: bool = True
        """ 是否使用代理 """
        self.proxy_pool: list[str] = []
        """ 代理池 """
        self.current_proxy: str | None = None
        """ 当前使用的代理 """
        self._init_proxy_pool()

        # 日志
        logger.debug(f"✔ 网页爬虫类实例化完成")

    def setup_session(self):
        """设置请求会话参数"""
        self.session.headers.update({"User-Agent": random.choice(_my_headers)})

        # 设置代理
        if self.use_proxy:
            self._set_random_proxy()

    def _init_proxy_pool(self):
        """初始化代理池 - 生成随机IP地址作为代理"""
        try:
            # 生成一些常用的代理IP地址（这里使用模拟的内网IP范围）
            # 在实际使用中，你可能需要从代理服务商获取真实的代理IP
            proxy_ips = []

            # 生成一些随机的IP地址（模拟代理池）
            for _ in range(10):
                # 生成192.168.x.x范围的IP（仅用于演示，实际使用需要真实代理）
                ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
                port = random.choice([8080, 3128, 8888, 9999, 1080])
                proxy_ips.append(f"{ip}:{port}")

            # 也可以添加一些公开的代理IP（需要验证可用性）
            # 注意：以下是示例IP，实际使用时需要替换为可用的代理
            public_proxies = [
                "103.152.112.162:80",
                "103.155.54.185:83",
                "103.159.46.25:83",
                "103.159.46.34:83",
                "103.159.46.46:83",
            ]

            self.proxy_pool = proxy_ips + public_proxies
            logger.debug(f"✔ 代理池初始化完成，共 {len(self.proxy_pool)} 个代理")

        except Exception as e:
            logger.debug(f"✘ 代理池初始化失败: {e}")
            self.proxy_pool = []

    def _set_random_proxy(self):
        """设置随机代理"""
        if not self.proxy_pool:
            logger.debug("代理池为空，跳过代理设置")
            return

        try:
            # 随机选择一个代理
            proxy = random.choice(self.proxy_pool)
            self.current_proxy = proxy

            # 设置代理配置
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",  # 注意：很多HTTP代理也可以处理HTTPS请求
            }

            self.session.proxies.update(proxy_dict)
            logger.debug(f"✔ 已设置代理: {proxy}")

        except Exception as e:
            logger.debug(f"✘ 设置代理失败: {e}")
            self.current_proxy = None

    def _generate_random_ip(self) -> str:
        """生成随机IP地址"""
        # 生成随机IP地址（避免使用保留IP段）
        # 这里使用一些常见的公网IP段
        ip_ranges = [(1, 126), (128, 191), (192, 223)]  # A类地址  # B类地址  # C类地址

        range_choice = random.choice(ip_ranges)
        first_octet = random.randint(range_choice[0], range_choice[1])

        # 避免一些特殊用途的IP段
        while first_octet in [
            127,
            169,
            172,
            192,
            224,
            225,
            226,
            227,
            228,
            229,
            230,
            231,
            232,
            233,
            234,
            235,
            236,
            237,
            238,
            239,
        ]:
            first_octet = random.randint(range_choice[0], range_choice[1])

        second_octet = random.randint(0, 255)
        third_octet = random.randint(0, 255)
        fourth_octet = random.randint(1, 254)

        return f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"

    def refresh_proxy_pool(self):
        """刷新代理池"""
        logger.debug("正在刷新代理池...")
        self._init_proxy_pool()

    def toggle_proxy(self, enable: bool | None = None):
        """开启/关闭代理功能"""
        if enable is None:
            self.use_proxy = not self.use_proxy
        else:
            self.use_proxy = enable

        if not self.use_proxy:
            # 清除代理设置
            self.session.proxies.clear()
            self.current_proxy = None
            logger.debug("✔ 代理功能已关闭")
        else:
            logger.debug("✔ 代理功能已开启")

    def get_current_proxy(self) -> str | None:
        """获取当前使用的代理"""
        return self.current_proxy

    def flush_runtime_cache_and_reset_state(self):
        """清除运行时临时缓存数据并重置状态"""
        self.current_crawling_web = ""
        self.current_crawling_article = ""
        self.crawling_log.clear()
        self.task_progress = 0.0
        self.current_state = State.IDLE
        # 重置代理相关状态
        if hasattr(self, "use_proxy"):
            self.current_proxy = None
        logger.debug("✔ 爬虫运行时缓存数据已清除，状态已重置")

    def check_robots_txt(self, url: str) -> bool:
        """检查robots.txt协议"""
        if not self.respect_robots_txt:
            return True
        parsed = urlparse(url)
        netloc = parsed.netloc

        # 使用缓存的解析器，如果不存在则尝试去拉取并解析 robots.txt
        rp = self._robots_parsers.get(netloc)
        if rp is None:
            try:
                self._fetch_and_parse_robots(netloc, parsed.scheme)
                rp = self._robots_parsers.get(netloc)
            except Exception:
                # 如果解析 robots.txt 发生错误，为了健壮性允许抓取
                return True

        if rp is None:
            return True

        try:
            # 使用 '*' 作为 user-agent 的默认策略
            return rp.can_fetch("*", url)
        except Exception:
            return True

    def _fetch_and_parse_robots(self, netloc: str, scheme: str = "https") -> None:
        """拉取并解析指定站点的 robots.txt，缓存解析器和常用规则。

        netloc: 域名 (包含端口时也包含端口部分)
        scheme: 协议，默认 https（在有些站点上 robots 文件在 http 下）
        """
        base_url = f"{scheme}://{netloc}"
        robots_url = urljoin(base_url, "/robots.txt")

        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)

        try:
            rp.read()
            # 缓存解析器
            self._robots_parsers[netloc] = rp

            # 解析 crawl-delay 和 disallow: 若站点对 '*' 有 disallow: /
            # urllib 的 RobotFileParser 没有直接暴露 crawl-delay，因此我们手动获取文本
            crawl_delay = None
            disallow_all = False
            try:
                # 直接请求 robots.txt 内容以解析 Crawl-delay
                resp = self.session.get(robots_url, timeout=5)
                if resp.status_code == 200 and resp.text:
                    ua = None
                    lines = [ln.strip() for ln in resp.text.splitlines()]
                    for line in lines:
                        if not line or line.startswith("#"):
                            continue
                        parts = [p.strip() for p in line.split(":", 1)]
                        if len(parts) != 2:
                            continue
                        key, val = parts[0].lower(), parts[1].strip()
                        if key == "user-agent":
                            ua = val
                        elif key == "crawl-delay" and (ua == "*" or ua is None):
                            try:
                                crawl_delay = float(val)
                            except Exception:
                                try:
                                    crawl_delay = int(val)
                                except Exception:
                                    crawl_delay = None
                        elif key == "disallow" and (ua == "*" or ua is None):
                            # 如果对 '*' 标记了 disallow: / 则视为禁止整个站点
                            if val == "/":
                                disallow_all = True
            except Exception:
                # 忽略解析错误，继续以 rp 的结果为准
                crawl_delay = None
                disallow_all = False

            self._site_rules[netloc] = {
                "crawl_delay": crawl_delay,
                "disallow_all": disallow_all,
            }
        except Exception:
            # 在无法读取 robots.txt 时不缓存，调用方会默认允许抓取
            if netloc in self._robots_parsers:
                del self._robots_parsers[netloc]
            self._site_rules.pop(netloc, None)

    def download_file(self, url: str, file_type: str) -> bytes | None:
        """下载特定类型文件"""
        if not self.check_robots_txt(url):
            logger.debug(f'✘ "{url}" 被 robots.txt 禁止抓取')
            return None

        try:
            response = self.session.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                # 文件内容类型验证
                content_type: str = response.headers.get("content-type", "")
                if self.validate_file_type(content_type, file_type):
                    return response.content
                logger.debug(f'✘ "{url}"文件类型不匹配, 实际文件类型: {content_type}')
                return None
            logger.debug(f'✘ "{url}"响应状态异常')
            return None
        except Exception as e:
            logger.debug(f'✘ "{url}"下载失败 : {e}')
            return None

    def validate_file_type(self, content_type: str, expected_type: str) -> bool:
        """验证文件类型匹配"""
        type_mapping: dict[str, str] = {
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
                # 在开始爬取站点前自动拉取并应用 robots.txt 规则
                try:
                    parsed: ParseResult = urlparse(website)
                    self._fetch_and_parse_robots(
                        parsed.netloc, parsed.scheme or "https"
                    )
                    rules = self._site_rules.get(parsed.netloc, {})
                    if rules.get("disallow_all"):
                        logger.info(
                            f"站点 {parsed.netloc} 在 robots.txt 中禁止抓取，已跳过"
                        )
                        continue
                except Exception as e:
                    logger.debug(f"拉取 robots.txt 失败，继续尝试抓取 {website}: {e}")

                self.crawl_website(website)

            return True
        except Exception as e:
            logger.debug(f"✘ 爬虫任务失败: {e}")
            return False
        finally:
            self.flush_runtime_cache_and_reset_state()

    def crawl_website(self, base_url: str):
        """爬取指定网站"""
        to_visit: set[str] = {base_url}
        while len(to_visit) > 0:
            self.current_state = State.CRAWLING
            url = to_visit.pop()

            if url in self.visited_urls:
                continue

            # 检查是否在黑名单中
            if self.is_blocked_site(url):
                continue

            self.visited_urls.add(url)
            try:
                logger.debug(f'正在访问URL: "{url}"')
                self.setup_session()  # 每次请求前更新User-Agent
                response: Response = self.session.get(
                    url, timeout=crawler_config.request_timeout
                )
                if response.status_code == 200:
                    logger.debug(f'✔ "{url}"访问成功')
                    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
                    # 将文件提取和保存逻辑分离
                    self.extract_and_save_files(soup, url)
                    # 提取链接以继续爬取
                    links: set[str] = self.extract_links(soup, base_url)
                    to_visit.update(links)
                else:
                    logger.debug(f'✘ "{url}"访问失败, 状态码: {response.status_code}')
                time.sleep(random.uniform(1, 3))  # 请求延迟

                # 每隔几个请求更换一次代理IP
                if self.use_proxy and len(self.visited_urls) % 3 == 0:
                    self._set_random_proxy()
            except Exception as e:
                logger.debug(f"✘ 访问失败 {url}: {e}")
        self.current_state = State.IDLE

    def is_blocked_site(self, url: str) -> bool:
        """检查URL是否在黑名单中"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        for blocked in crawler_config.blocked_sites:
            if blocked in domain or blocked in url:
                return True
        return False

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> set[str]:
        """从页面提取链接"""
        links: set[str] = set()
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
                    logger.debug(f'发现链接: "{full_url}"')
                    links.add(full_url)
        return links

    def extract_and_save_files(self, soup: BeautifulSoup, page_url: str):
        """提取并保存文件"""
        # 查找所有可能的文件链接
        all_links: list[Tag | PageElement | NavigableString] | None = soup.find_all(
            "a", href=True
        )

        for link in all_links:
            if link is None:
                continue
            if isinstance(link, Tag):
                href: str = str(link.get("href", ""))
                if href == "":
                    continue

                full_url: str = urljoin(page_url, href)

                # 检查url中是否携带目标文件类型
                for file_type in crawler_config.file_type:
                    if file_type in full_url.lower():
                        # 检查关键词
                        if self.match_keywords(link.text, soup):
                            self.current_crawling_article = (
                                link.text or os.path.basename(urlparse(full_url).path)
                            )
                            logger.debug(f"正在处理文件链接: {full_url}")
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
            file_content: bytes | None = self.download_file(url, file_type)
            if isinstance(file_content, bytes):
                self.save_file(file_content, url, file_type)
            else:
                logger.debug(f'✘ 文件下载失败或类型不匹配 "{url}"')
        except Exception as e:
            logger.debug(f"✘ 下载和保存文件失败 {url}: {e}")

    def save_file(self, content: bytes, url: str, file_type: str):
        """保存文件到指定目录"""
        try:
            # 生成时间戳
            timestamp: str = datetime.now().strftime("%Y%m%d")

            # 创建按类型和时间分类的目录
            file_type_name: str = file_type.upper().replace(".", "")
            save_dir: Path = self.resource_path / file_type_name / timestamp
            save_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            filename: str = os.path.basename(urlparse(url).path)
            if not filename or filename == "":
                filename = f"{self.total_files_downloaded}{file_type}"

            file_path: Path = save_dir / filename

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(content)

            self.total_files_downloaded += 1

            # 记录到日志
            logger.debug(f'✔ 保存文件:"{file_path}"\tURL:"{url}"')

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
