from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import re
from .web_crawler import *
from .crawling_config import CrawlingConfig


class TaskScheduler:
    def __init__(self, crawling_config: CrawlingConfig):
        self.config = crawling_config
        self.scheduler = BackgroundScheduler()
        self.crawler = WebCrawler(crawling_config)

    def parse_trigger_time(self):
        """解析触发时间配置"""
        time_str = self.config.trigger_time
        match = re.match(r"(\d{1,2}):(\d{2})(AM|PM),UTC([+-])(\d{2}):(\d{2})", time_str)

        if match:
            hour, minute, am_pm, tz_sign, tz_hour, tz_minute = match.groups()
            hour = int(hour)
            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0

            return hour, int(minute)
        return 8, 0  # 默认时间

    def start_scheduling(self):
        """启动定时任务"""
        hour, minute = self.parse_trigger_time()

        # 添加每日定时任务
        self.scheduler.add_job(
            self.crawler.start_crawling_task,
            "cron",
            hour=hour,
            minute=minute,
            id="daily_crawling",
        )

        # 启动调度器
        self.scheduler.start()
