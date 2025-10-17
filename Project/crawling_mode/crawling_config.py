import json
import re
from datetime import datetime

from dataclasses import dataclass, field
from typing_extensions import Self
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CrawlingConfig:
    trigger_time: str = field(default="8:00AM,UTC+08:00")
    crawling_source_list: list = field(
        default_factory=lambda: [
            "https://arxiv.org/catchup/cs.CV/2025-09-30?abs=True",
            "https://scholar.google.com/?hl=zh-CN",
        ]
    )
    blocked_sites: list[str] = field(default_factory=lambda: ["example.com/restricted"])
    crawling_keywords: list[str] = field(
        default_factory=lambda: ["[Pp]aper", "[Ee]ssay"]
    )
    file_type: list[str] = field(
        default_factory=lambda: [".pdf", ".txt", ".jpg", ".png"]
    )
    timeliness: int = field(default=365)
    max_workers: int = field(default=5)
    request_timeout: int = field(default=30)
    retry_attempts: int = field(default=3)

    def __init__(self, config_path="crawling_config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """加载并验证配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.validate_config(config)
            return config
        except Exception as e:
            print(f"配置加载错误: {e}")
            return self.get_default_config()

    def validate_config(self, config):
        """验证配置参数有效性"""
        # 时间格式验证
        time_pattern = r"(\d{1,2}):(\d{2})(AM|PM),UTC[+-](\d{2}):(\d{2})"
        if not re.match(time_pattern, config.get("trigger_time", "")):
            raise ValueError("时间格式错误")

        # 文件类型验证
        valid_types = [".pdf", ".txt", ".jpg", ".png", ".doc", ".docx"]
        for file_type in config.get("file_type", []):
            if file_type not in valid_types:
                raise ValueError(f"不支持的文件类型: {file_type}")

    @classmethod
    def get_default_config(cls) -> "CrawlingConfig":
        """返回默认配置"""
        return cls()
