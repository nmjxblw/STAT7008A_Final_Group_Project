"""
异常处理模块 - Exception Handler
"""

import time
import logging
import traceback
from functools import wraps
from datetime import datetime
from pathlib import Path
import requests
from .crawling_config import CrawlingConfig


class CrawlerException(Exception):
    """爬虫基础异常类"""

    pass


class ConfigException(CrawlerException):
    """配置异常"""

    pass


class NetworkException(CrawlerException):
    """网络异常"""

    pass


class FileException(CrawlerException):
    """文件操作异常"""

    pass


class ExceptionHandler:
    """异常处理器"""

    def __init__(self, config: CrawlingConfig = None, log_dir: str = None):
        """初始化异常处理器"""
        self.max_retries: int = config.retry_attempts if config else 3
        self.timeout: int = config.request_timeout if config else 30

        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "Logs" / "Exceptions"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 配置日志
        log_file = self.log_dir / f"exception_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.ERROR,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def robust_request(
        self, url: str, retry_count: int = 0
    ) -> requests.Response | None:
        """带重试机制的请求处理"""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                wait_time = 2**retry_count  # 指数退避
                time.sleep(wait_time)
                return self.robust_request(url, retry_count + 1)
            else:
                self.log_exception(e, f"请求失败: {url}")
                raise NetworkException(f"请求失败 after {self.max_retries} 次重试: {e}")

    def log_exception(self, exception: Exception, context: str = ""):
        """记录异常"""
        error_msg = f"Context: {context}\nException: {str(exception)}\nTraceback:\n{traceback.format_exc()}"
        self.logger.error(error_msg)
        print(f"❌ 错误: {str(exception)}")

    def handle_exception(
        self, exception: Exception, context: str = "", raise_error: bool = False
    ):
        """处理异常"""
        self.log_exception(exception, context)
        if raise_error:
            raise exception


def exception_handler(context: str = "", raise_error: bool = False):
    """异常处理装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ExceptionHandler()
                handler.handle_exception(
                    e,
                    context=context or f"Function: {func.__name__}",
                    raise_error=raise_error,
                )
                return None

        return wrapper

    return decorator
