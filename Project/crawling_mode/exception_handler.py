import time
import requests
from .crawling_config import CrawlingConfig


class ExceptionHandler:
    def __init__(self, config: CrawlingConfig):
        self.max_retries: int = config.retry_attempts
        self.timeout: int = config.request_timeout

    def robust_request(
        self, url: str, retry_count: int = 0
    ) -> requests.Response | None:
        """带重试机制的请求处理[11](@ref)"""
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
                raise Exception(f"请求失败 after {self.max_retries} 次重试: {e}")
