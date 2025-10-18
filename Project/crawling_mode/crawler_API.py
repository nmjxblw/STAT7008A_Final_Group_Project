from flask import Flask, jsonify
import threading
import time
from .web_crawler import WebCrawler


class CrawlerAPI:
    def __init__(self, crawler: WebCrawler):
        self.app: Flask = Flask(__name__)
        self.crawler: WebCrawler = crawler
        self.setup_routes()
        self.current_status: str = "idle"
        self.progress: float = 0.0

    def setup_routes(self):
        """设置API路由"""
        self.app.add_url_rule(
            "/start", "start_crawling_task", self.start_crawling_task, methods=["POST"]
        )
        self.app.add_url_rule(
            "/status/current_web",
            "get_current_crawling_web",
            self.get_current_crawling_web,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/status/current_article",
            "get_current_crawling_article",
            self.get_current_crawling_article,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/status/progress",
            "get_crawling_task_progress",
            self.get_crawling_task_progress,
            methods=["GET"],
        )

    def start_crawling_task(self):
        """启动爬虫任务API接口"""
        if self.current_status == "running":
            return jsonify({"status": "error", "message": "任务已在进行中"})

        def run_crawler():
            self.current_status = "running"
            self.progress = 0.0
            try:
                success = self.crawler.start_crawling_task()
                return success
            finally:
                self.current_status = "idle"
                self.progress = 100.0

        thread = threading.Thread(target=run_crawler)
        thread.start()

        return jsonify({"status": "success", "message": "爬虫任务已启动"})

    def get_current_crawling_web(self):
        """获取当前爬取的网站"""
        return jsonify(
            {
                "current_web": getattr(self.crawler, "current_web", "暂无"),
                "status": self.current_status,
            }
        )

    def get_crawling_task_progress(self):
        """获取任务进度"""
        return jsonify({"progress": self.progress, "status": self.current_status})

    def run_api_server(self, host="localhost", port=5000):
        """启动API服务器"""
        self.app.run(host=host, port=port, debug=False)
