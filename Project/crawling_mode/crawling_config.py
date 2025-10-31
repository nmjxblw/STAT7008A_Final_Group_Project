"""爬虫配置数据类及其JSON文件加载/保存功能"""

import json
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List
from dataclasses_json import dataclass_json
import os


@dataclass_json
@dataclass
class CrawlingConfig:
    """爬取配置数据类"""

    trigger_time: str = field(default="8:00AM,UTC+08:00")
    """每天触发自动爬取的时间，格式如 "8:00AM,UTC+08:00" """
    crawling_source_list: List[str] = field(
        default_factory=lambda: ["https://arxiv.org/catchup/cs.CV/2025-09-30?abs=True"]
    )
    """爬取来源网站列表"""
    blocked_sites: List[str] = field(default_factory=lambda: ["config from code"])
    """被阻止的网站列表"""
    crawling_keywords: List[str] = field(
        default_factory=lambda: ["[Pp]aper", "[Ee]ssay"]
    )
    """爬取关键词列表，支持正则表达式"""
    file_type: List[str] = field(default_factory=lambda: [".pdf"])
    """允许下载的文件类型列表"""
    timeliness: int = field(default=365)
    """文件时效性，单位为天"""
    max_workers: int = field(default=5)
    """最大并发工作线程数"""
    request_timeout: int = field(default=5)
    """请求超时时间，单位为秒"""
    retry_attempts: int = field(default=3)
    """请求重试次数"""

    def __post_init__(self):
        """
        在数据类自动生成的 __init__ 方法后调用，用于验证数据。
        确保任何方式创建的实例都经过验证。
        """
        self._validate_trigger_time()
        self._validate_file_types()

    def _validate_trigger_time(self):
        """验证 trigger_time 字段的格式"""
        # 移除可能存在的空格
        self.trigger_time = self.trigger_time.replace(" ", "")

        # 定义多种可能的时间格式模式
        patterns = [
            # 尝试匹配带时区的格式 (e.g., "8:00AM,UTC+08:00" or "14:30-05:00")
            r"^(\d{1,2}:\d{2}\s*(AM|PM)?)\s*,\s*(UTC)?([+-]\d{2}:\d{2})$",
            # 尝试匹配简单时间格式 (e.g., "8:00" or "14:30")
            r"^(\d{1,2}:\d{2})\s*(AM|PM)?$",
        ]

        for pattern in patterns:
            if re.match(pattern, self.trigger_time, re.IGNORECASE):
                # 如果匹配成功一种模式，则验证通过
                return

        # 如果所有模式都不匹配，则抛出异常
        raise ValueError(
            f"无效的时间格式: '{self.trigger_time}'。期望格式类似 '8:00AM,UTC+08:00' 或 '14:30'"
        )

    def _validate_file_types(self):
        """验证 file_type 字段是否包含支持的文件类型"""
        valid_types = {".pdf", ".txt", ".jpg", ".png", ".doc", ".docx", ".xls", ".xlsx"}
        for ext in self.file_type:
            if ext not in valid_types:
                raise ValueError(
                    f"不支持的文件类型: '{ext}'. 支持的类型有: {', '.join(sorted(valid_types))}"
                )

    @classmethod
    def from_json_file(
        cls, config_path: str = "crawling_config.json"
    ) -> "CrawlingConfig":
        """
        类工厂方法：从JSON文件创建CrawlingConfig实例。
        清晰地将文件加载逻辑与数据类本身的职责分离开
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            # 使用 dataclasses_json 提供的方法从字典创建实例
            instance = cls.from_dict(  # pyright: ignore[reportAttributeAccessIssue]
                config_data
            )
            # 注意：__post_init__ 会在 from_dict 后自动调用，从而执行验证
            return instance
        except FileNotFoundError:
            print(f"配置文件 {config_path} 未找到，使用默认配置。")
            return cls()  # 返回默认配置实例
        except json.JSONDecodeError as e:
            print(f"配置文件 JSON 格式错误: {e}，使用默认配置。")
            return cls()
        except Exception as e:
            print(f"加载配置时发生错误: {e}，使用默认配置。")
            return cls()

    def to_json_file(self, crawling_config_file_name: str = "crawling_config.json"):
        """
        将当前配置实例保存到JSON文件中。
        提供一种简单的方法来持久化配置更改
        """
        try:
            with open(
                os.path.join(os.getcwd(), crawling_config_file_name),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    self.to_dict(),  # pyright: ignore[reportAttributeAccessIssue]
                    f,
                    ensure_ascii=False,
                    indent=4,
                )
        except Exception as e:
            print(f"保存配置时发生错误: {e}")


# 导入模块时自动加载配置
crawling_config = CrawlingConfig.from_json_file("./crawling_config.json")
if __name__ == "__main__":
    print(crawling_config)
