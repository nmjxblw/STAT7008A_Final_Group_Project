"""爬虫模块 - 网页爬虫类实现"""

import enum
import random
import threading
from typing import Sequence
from requests import Response
import requests
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import queue
from bs4 import BeautifulSoup, PageElement, NavigableString, Tag
import urllib.robotparser
from urllib.parse import ParseResult, ParseResultBytes, urljoin, urlparse
import time
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from global_module import crawler_config, USING_PROXY
from utility_module import SingletonMeta
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
        # 代理相关配置
        self.use_proxy: bool = USING_PROXY
        """ 是否使用代理 """
        print(f"代理功能启用状态: {self.use_proxy}")
        self.proxy_pool: list[str] = []
        """ 代理池 """
        self.current_proxy: str = ""
        """ 当前使用的代理 """
        self._init_proxy_pool()
        self.session: requests.Session = requests.Session()
        """ 请求会话（主线程用） """
        self.setup_session()
        self.origin_url: str = ""
        """ 原始源节点URL """

        # 线程安全的数据结构
        self._pending_urls: queue.Queue = queue.Queue()
        """ 待访问的URL队列（线程安全） """
        self.visited_urls: set[str] = set()
        """ 已访问的URL集合 """
        self._visited_urls_lock: threading.RLock = threading.RLock()
        """ 已访问URL集合的锁 """

        self.respect_robots_txt: bool = True
        """ 是否遵守robots.txt协议 """
        self.current_crawling_web: str = ""
        """ 当前正在爬取的网页 """
        self.current_crawling_article: str = ""
        """ 当前正在爬取的文章 """
        self.total_files_downloaded: int = 0
        """ 已下载的文件总数 """
        self._download_count_lock: threading.RLock = threading.RLock()
        """ 下载计数锁 """
        self.crawling_log: list[dict] = []
        """ 爬取日志列表 """
        self._log_lock: threading.RLock = threading.RLock()
        """ 日志列表锁 """

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

        self.max_threads: int = min(
            os.cpu_count() or 4, 8
        )  # 限制最大线程数避免过多并发
        """ 最大线程数 """
        self._thread_pool: ThreadPoolExecutor | None = None
        """ 线程池实例 """
        self._active_futures: list = []
        """ 活跃的 Future 对象列表 """

        # robots.txt 解析器缓存: netloc -> RobotFileParser
        self._robots_parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
        """ robots.txt 解析器缓存 """
        self._robots_cache_lock: threading.RLock = threading.RLock()
        """ robots.txt 缓存锁 """

        # site-specific rules cache: netloc -> {crawl_delay: float|None, disallow_all: bool}
        self._site_rules = {}
        """ 站点特定规则缓存 """

        logger.debug(f"✔ 网页爬虫类实例化完成")

    def setup_session(self):
        """设置请求会话参数"""
        self.session.headers.update(
            {"User-Agent": random.choice(crawler_config.headers.to_list())}
        )

        # 设置代理
        if self.use_proxy:
            self._set_random_proxy()
        else:
            logger.debug("✔ 代理功能未启用，跳过代理设置")

    def _create_worker_session(self) -> requests.Session:
        """为工作线程创建独立的 requests.Session"""
        session = requests.Session()
        session.headers.update(
            {"User-Agent": random.choice(crawler_config.headers.to_list())}
        )

        # 为工作线程设置随机代理
        if self.use_proxy and self.proxy_pool:
            proxy = random.choice(self.proxy_pool)
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }
            session.proxies.update(proxy_dict)

        return session

    def _init_proxy_pool(self):
        """初始化代理池 - 生成随机IP地址作为代理"""
        if not self.use_proxy:
            logger.debug("✔ 代理功能未启用，跳过代理池初始化")
            return
        try:

            self.proxy_pool = crawler_config.public_proxies.to_list()
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
            proxy: str = random.choice(self.proxy_pool)
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
            self.current_proxy = ""

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
            self.current_proxy = ""
            logger.debug("✔ 代理功能已关闭")
        else:
            logger.debug("✔ 代理功能已开启")

    def get_current_proxy(self) -> str:
        """获取当前使用的代理"""
        return self.current_proxy

    def flush_runtime_cache_and_reset_state(self):
        """清除运行时临时缓存数据并重置状态"""
        self.current_crawling_web = ""
        self.current_crawling_article = ""

        # 清空队列
        while not self._pending_urls.empty():
            try:
                self._pending_urls.get_nowait()
            except queue.Empty:
                break

        # 清空其他数据结构
        with self._visited_urls_lock:
            self.visited_urls.clear()
        with self._log_lock:
            self.crawling_log.clear()
        with self._download_count_lock:
            self.total_files_downloaded = 0

        self.task_progress = 0.0
        self.current_state = State.IDLE

        # 清理线程池
        if self._thread_pool:
            self._thread_pool.shutdown(wait=False)
            self._thread_pool = None
        self._active_futures.clear()

        # 重置代理相关状态
        if hasattr(self, "use_proxy"):
            self.current_proxy = ""
        logger.debug("✔ 爬虫运行时缓存数据已清除，状态已重置")

    def _add_url_to_pending(self, url: str) -> None:
        """线程安全地添加URL到待处理队列"""
        self._pending_urls.put(url)

    def _add_urls_to_pending(self, urls: set[str]) -> None:
        """线程安全地批量添加URL到待处理队列"""
        for url in urls:
            self._pending_urls.put(url)

    def _is_url_visited(self, url: str) -> bool:
        """线程安全地检查URL是否已被访问"""
        with self._visited_urls_lock:
            return url in self.visited_urls

    def _mark_url_visited(self, url: str) -> bool:
        """线程安全地标记URL为已访问，返回True如果是首次访问"""
        with self._visited_urls_lock:
            if url in self.visited_urls:
                return False
            self.visited_urls.add(url)
            return True

    def _increment_download_count(self) -> None:
        """线程安全地增加下载计数"""
        with self._download_count_lock:
            self.total_files_downloaded += 1

    def _add_to_crawling_log(self, log_entry: dict) -> None:
        """线程安全地添加爬取日志"""
        with self._log_lock:
            self.crawling_log.append(log_entry)

    def check_robots_txt(self, url: str) -> bool:
        """检查robots.txt协议（线程安全）"""
        if not self.respect_robots_txt:
            return True
        parsed: ParseResult = urlparse(url)
        netloc: str = parsed.netloc

        # 使用缓存的解析器，如果不存在则尝试去拉取并解析 robots.txt
        with self._robots_cache_lock:
            rp: urllib.robotparser.RobotFileParser | None = self._robots_parsers.get(
                netloc
            )

        if rp is None:
            try:
                self._fetch_and_parse_robots(netloc, parsed.scheme)
                with self._robots_cache_lock:
                    rp = self._robots_parsers.get(netloc)
            except Exception:
                # 如果解析 robots.txt 发生错误，为了健壮性允许抓取
                logger.debug(f"✘ 解析 robots.txt 失败，允许抓取 {url}")
                pass
            return True

        try:
            # 使用 '*' 作为 user-agent 的默认策略
            return rp.can_fetch("*", url)
        except Exception:
            # 出现异常时允许抓取
            logger.debug(f"✘ 检查 robots.txt 失败，允许抓取 {url}")
            return True

    def _fetch_and_parse_robots(self, netloc: str, scheme: str = "https") -> None:
        """拉取并解析指定站点的 robots.txt，缓存解析器和常用规则（线程安全）。

        参数:
            netloc: 域名 (包含端口时也包含端口部分)
            scheme: 协议，默认 https（在有些站点上 robots 文件在 http 下）
        """
        # 使用锁避免重复获取同一站点的 robots.txt
        with self._robots_cache_lock:
            # 双重检查避免重复工作
            if netloc in self._robots_parsers:
                return

            base_url = f"{scheme}://{netloc}"
            robots_url = urljoin(base_url, "/robots.txt")

            rp: urllib.robotparser.RobotFileParser = (
                urllib.robotparser.RobotFileParser()
            )
            rp.set_url(robots_url)

            try:
                # 使用临时session避免影响主session
                temp_session = self._create_worker_session()
                rp.read()
                # 缓存解析器
                self._robots_parsers[netloc] = rp

                # 解析 crawl-delay 和 disallow: 若站点对 '*' 有 disallow: /
                # urllib 的 RobotFileParser 没有直接暴露 crawl-delay，因此我们手动获取文本
                crawl_delay: float = 1.0
                disallow_all: bool = False
                try:
                    # 直接请求 robots.txt 内容以解析 Crawl-delay
                    resp: requests.Response = temp_session.get(robots_url, timeout=5)
                    if resp.status_code == 200 and resp.text:
                        ua: str | None = None
                        lines: list[str] = [ln.strip() for ln in resp.text.splitlines()]
                        for line in lines:
                            if not line or line.startswith("#"):
                                # 跳过空行和注释
                                continue
                            parts = [
                                p.strip() for p in line.split(":", 1)
                            ]  # 分割成键值对,最多分割一次
                            if len(parts) != 2:
                                # 格式错误，跳过
                                continue
                            key, val = parts[0].lower(), parts[1].strip()
                            if key == "user-agent":
                                ua = val
                            elif key == "crawl-delay" and (ua == "*" or ua is None):
                                try:
                                    crawl_delay = float(val)
                                except Exception:
                                    crawl_delay = 1.0

                            elif key == "disallow" and (ua == "*" or ua is None):
                                # 如果对 '*' 标记了 disallow: / 则视为禁止整个站点
                                if val == "/":
                                    disallow_all = True
                except Exception:
                    # 忽略解析错误，继续以 rp 的结果为准
                    crawl_delay = 1.0
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
            logger.debug(f'✘ 尝试下载 "{url}" ，但被 robots.txt 禁止抓取')
            return None

        try:
            logger.debug(f'正在下载文件: "{url}" 类型[ {file_type} ]')
            response: requests.Response = self.session.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                # 文件内容类型验证
                content_type: str = response.headers.get("content-type", "")
                if self.validate_file_type(content_type, file_type):
                    if isinstance(response.content, bytes):
                        logger.debug(f'✔ "{url}"流式二进制数据下载成功')
                        return response.content
                    else:
                        logger.debug(f'✘ "{url}"文件内容非二进制数据')
                        return None
                else:
                    logger.debug(
                        f'✘ "{url}"文件类型不匹配, 实际文件类型: {content_type}'
                    )
                    return None
            else:
                logger.debug(f'✘ "{url}"响应状态异常')
                return None
        except Exception as e:
            logger.debug(f'✘ "{url}"下载失败 : {e}')
            return None

    def validate_file_type(self, content_type: str, expected_type: str) -> bool:
        """验证文件类型匹配"""
        type_mapping: dict[str, str] = {
            "pdf": "application/pdf",
            "txt": "text/plain",
            "jpg": "image/jpeg",
            "png": "image/png",
        }
        expected_mime = type_mapping.get(expected_type, "")
        return expected_mime in content_type

    def start_crawling_task(self) -> bool:
        """启动爬虫任务（多线程版本）"""
        try:
            # 创建保存目录和日志目录
            self.resource_path.mkdir(parents=True, exist_ok=True)

            # 创建线程池
            self._thread_pool = ThreadPoolExecutor(
                max_workers=self.max_threads, thread_name_prefix="crawler_worker"
            )

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
                            f"✘ 站点 {parsed.netloc} 在 robots.txt 中禁止抓取，已跳过..."
                        )
                        continue
                except Exception as e:
                    logger.debug(f"拉取 robots.txt 失败，继续尝试抓取 {website}: {e}")

                self.current_state = State.CRAWLING
                self._add_url_to_pending(website)
                self.origin_url = website
                self.crawl_website_multithread()

            return True
        except Exception as e:
            logger.debug(f"✘ 爬虫任务失败: {e}")
            return False
        finally:
            # 清理线程池
            if self._thread_pool:
                self._thread_pool.shutdown(wait=True)
            self.flush_runtime_cache_and_reset_state()

    def crawl_website_multithread(self):
        """多线程爬取指定网站"""
        processed_count = 0

        while not self._pending_urls.empty():
            # 批量获取待处理的URL
            batch_urls: list[str] = []
            batch_size: int = min(self.max_threads * 2, 20)  # 每批处理的URL数量

            for _ in range(batch_size):
                try:
                    url = self._pending_urls.get_nowait()
                    if not self._is_url_visited(url) and not self.is_blocked_site(url):
                        batch_urls.append(url)
                        processed_count += 1
                    else:
                        logger.debug(f'✘ "{url}"已访问或在黑名单中，跳过...')
                except queue.Empty:
                    break

            if not batch_urls:
                break

            # 提交批量任务到线程池
            futures: list[Future] = []
            for url in batch_urls:
                if self._thread_pool:
                    future = self._thread_pool.submit(self._crawl_single_url, url)
                    futures.append(future)
                    self._active_futures.append(future)

            # 等待所有任务完成并处理结果
            for future in as_completed(futures):
                try:
                    extracted_links = future.result(timeout=30)  # 30秒超时
                    if extracted_links:
                        self._add_urls_to_pending(extracted_links)
                except Exception as e:
                    logger.debug(f"✘ 爬取任务执行失败: {e}")
                finally:
                    # 清理已完成的future
                    if future in self._active_futures:
                        self._active_futures.remove(future)

            # 添加批处理间的延迟，避免过于频繁的请求
            time.sleep(random.uniform(0.5, 2.0))

        self.current_state = State.COMPLETED
        logger.debug(f"✔ 网站爬取完成，处理了 {processed_count} 个URL")

    def _crawl_single_url(self, url: str) -> set[str] | None:
        """单个URL爬取工作函数（工作线程执行）"""
        try:
            # 标记URL为已访问
            if not self._mark_url_visited(url):
                return None  # URL已被其他线程处理

            # 检查robots.txt
            if not self.check_robots_txt(url):
                logger.debug(f'✘ "{url}" 被 robots.txt 禁止抓取')
                return None

            # 创建工作线程专用的session
            session = self._create_worker_session()

            logger.debug(f'正在处理URL: "{url}"')
            response: Response = session.get(
                url, stream=True, timeout=crawler_config.request_timeout
            )

            if response.status_code == 200:
                logger.debug(f'✔ "{url}"访问成功')
                soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
                # 将文件提取和保存逻辑分离
                links: set[str] = self.extract_links_and_save_files(soup, url)

                # 添加请求延迟
                time.sleep(random.uniform(1, 3))
                return links
            else:
                logger.debug(f'✘ "{url}"访问失败, 状态码: {response.status_code}')
                return None

        except Exception as e:
            logger.debug(f"✘ 访问失败 {url}: {e}")
            return None

    def is_blocked_site(self, url: str) -> bool:
        """检查URL是否在黑名单中"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        for blocked in crawler_config.blocked_sites:
            if blocked in domain or blocked in url:
                return True
        return False

    def extract_links_and_save_files(
        self, soup: BeautifulSoup, page_url: str
    ) -> set[str]:
        """提取潜在链接并保存文件"""
        logger.debug(f'正在从"{page_url}"中提取链接...')
        links: set[str] = set()
        # 查找所有可能的文件链接
        anchors: Sequence[Tag] = soup.find_all(name="a", href=True)
        """ HTML锚点元素列表 """
        if len(anchors) == 0:
            logger.debug(f'✘ "{page_url}"中未发现任何<a>标签，跳过文件提取...')
            return links
        for anchor in anchors:
            if anchor is None:
                continue
            href: str = str(anchor.get("href", ""))
            # 跳过空链接和锚点链接
            if href == "" or href.startswith("#"):
                continue
            full_url: str = urljoin(page_url, href)
            _is_file_link: bool = anchor.get("download") is not None
            # 检查url中是否携带目标文件类型
            for file_type in crawler_config.file_type.to_list():
                if isinstance(file_type, str):
                    file_type = file_type.lower().replace(r"[^a-z0-9]", "")
                    if file_type in full_url.strip().lower():
                        _is_file_link = True  # 识别为文件链接
                        # 检查关键词
                        if self.match_keywords(anchor.text, soup):
                            self.download_and_save_file(full_url, file_type)
                        # 只处理第一个匹配的文件类型
                        break
            if (
                urlparse(full_url).netloc == urlparse(self.origin_url).netloc
                and not _is_file_link
            ):
                logger.debug(f'从"{page_url}"发现新链接: "{full_url}"')
                links.add(full_url)
        return links

    def match_keywords(self, text: str, soup: BeautifulSoup) -> bool:
        """匹配关键词"""
        keywords_list: list[str] = crawler_config.crawling_keywords.to_list()
        if len(keywords_list) == 0:
            return True  # 如果没有设置关键词,则匹配所有

        # 获取链接文本和周围文本
        search_text = text + " " + soup.get_text()

        for keyword in keywords_list:
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
        finally:
            self._mark_url_visited(url)

    def save_file(self, content: bytes, url: str, file_type: str):
        """保存文件到指定目录（线程安全）"""
        try:
            # 生成时间戳
            timestamp: str = datetime.now().strftime("%Y%m%d")

            # 创建按类型和时间分类的目录
            file_type_name: str = file_type.upper().replace(r"[^A-Z0-9]", "")
            save_dir: Path = self.resource_path / file_type_name  # / timestamp
            save_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名（使用当前计数值避免线程竞争）
            filename: str = os.path.basename(urlparse(url).path)
            if not filename or filename == "":
                with self._download_count_lock:
                    filename = f"{self.total_files_downloaded}.{file_type}"
            # 确保文件名有正确的扩展名
            if not filename.endswith(f".{file_type}"):
                with self._download_count_lock:
                    filename = f"{filename}.{file_type}"
            self.current_crawling_article = filename
            file_path: Path = save_dir / filename

            if file_path.exists():
                logger.debug(f'✘ 同名文件已存在，跳过保存: "{file_path}"')
                return
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(content)

            # 线程安全地增加计数
            self._increment_download_count()

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
        """获取爬取工作进度（线程安全）"""
        if not crawler_config.crawling_source_list:
            return 0.0

        with self._visited_urls_lock:
            visited_count = len(self.visited_urls)

        # 简单的进度计算: 已访问URL数 / 预估总URL数
        # 这是一个简化的实现
        return min(
            100.0,
            (visited_count / max(1, len(crawler_config.crawling_source_list) * 10))
            * 100,
        )

    def get_block_list(self) -> list[str]:
        """获取当前的黑名单列表"""
        if isinstance(crawler_config.blocked_sites.to_list(), list):
            return crawler_config.blocked_sites.to_list()
        return []
