"""
高级日志配置模块
支持按日期创建文件夹，按时间命名日志文件
"""

import sys
import os
from io import TextIOWrapper
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from global_module import PROJECT_NAME


class _FileHandler(logging.Handler):
    """
    自定义日志处理器
    按日期创建目录，按启动时间创建日志文件
    """

    def __init__(
        self,
        base_dir: str = "logs",
        encoding: str = "utf-8",
        level: int = logging.DEBUG,
    ):
        """
        初始化处理器

        参数:
            base_dir: 日志根目录
            encoding: 文件编码
            level: 日志级别
        """
        super().__init__(level)

        self.base_dir: Path = Path(base_dir)
        """日志根目录"""
        self.encoding: str = encoding
        """文件编码"""
        self.stream: Optional[TextIOWrapper] = None
        """日志文件流"""
        self.current_date: Optional[str] = None
        """当前日志日期"""
        self.log_file_path: Optional[Path] = None
        """当前日志文件路径"""
        # 在初始化时就创建日志文件
        self._setup_log_file()

    def _setup_log_file(self):
        """设置日志文件"""
        # 获取当前日期和时间
        app_timestamp: datetime = datetime.now()
        """应用启动时间"""
        date_str: str = app_timestamp.strftime(r"%Y%m%d")
        """当前日期字符串"""
        time_str: str = app_timestamp.strftime(r"%H%M%S_%f")[:-3]  # 毫秒保留3位
        """当前时间字符串"""
        # 创建日期文件夹
        date_dir: Path = self.base_dir / date_str
        """日期目录路径"""
        date_dir.mkdir(parents=True, exist_ok=True)

        # 创建日志文件路径
        self.log_file_path = date_dir / f"{time_str}.log"
        self.current_date = date_str

        # 打开文件流
        self.stream: Optional[TextIOWrapper] = open(
            self.log_file_path, "a", encoding=self.encoding
        )
        # os.system("cls" if os.name == "nt" else "clear")
        print(f"✓ 日志文件已创建: {self.log_file_path}")

    def emit(self, record):
        """
        输出日志记录

        参数:
            record: 日志记录对象
        """
        try:
            # 检查日期是否改变（跨天处理）
            current_date = datetime.now().strftime("%Y%m%d")
            if current_date != self.current_date:
                # 关闭旧文件
                if self.stream:
                    self.stream.close()
                    self.stream = None
                # 创建新文件
                self._setup_log_file()

            # 确保 stream 已准备好（避免类型检查器认为可能为 None）
            if self.stream is None:
                self._setup_log_file()

            # 格式化并写入日志
            msg: str = self.format(record)
            if self.stream:
                self.stream.write(msg + "\n")
                self.stream.flush()

        except Exception:
            self.handleError(record)

    def close(self):
        """关闭处理器"""
        if self.stream:
            self.stream.close()
        super().close()


class LoggerConfig:
    """日志配置类"""

    def __init__(
        self,
        base_dir: str = "logs",
        log_format: str = r"[%(asctime)s.%(msecs)03d][%(pathname)s:%(lineno)d][%(levelname)s]"
        + os.linesep
        + r"%(message)s"
        + os.linesep,
        date_format: str = r"%Y-%m-%d %H:%M:%S",
        level: int = logging.DEBUG,
        encoding: str = "utf-8",
        console_output: bool = True,
    ):
        """
        初始化日志配置

        参数:
            base_dir: 日志根目录
            log_format: 日志格式
            date_format: 时间格式
            level: 日志级别
            encoding: 文件编码
            console_output: 是否同时输出到控制台
        """
        self.base_dir = base_dir
        """日志根目录"""
        self.log_format = log_format
        """日志格式"""
        self.date_format = date_format
        """时间格式"""
        self.level = level
        """日志级别"""
        self.encoding = encoding
        """文件编码"""
        self.console_output = console_output
        """是否同时输出到控制台"""

        # 确保日志根目录存在
        Path(base_dir).mkdir(parents=True, exist_ok=True)

    def get_logger(self, name: str = PROJECT_NAME) -> logging.Logger:
        """
        获取配置好的日志记录器

        参数:
            name: 日志记录器名称

        返回:
            配置好的日志记录器
        """
        # 创建日志记录器
        logger = logging.getLogger(name)
        """日志记录器对象"""
        logger.setLevel(self.level)

        # 清除已有的处理器（避免重复）
        logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(fmt=self.log_format, datefmt=self.date_format)
        """日志格式化器"""
        # 添加文件处理器
        file_handler = _FileHandler(
            base_dir=self.base_dir, encoding=self.encoding, level=self.level
        )
        """文件处理器"""
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 添加控制台处理器（可选）
        if self.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger


def setup_logger(
    name: str = "AppLogger",
    base_dir: str = "logs",
    level: int = logging.DEBUG,
    console_output: bool = True,
) -> logging.Logger:
    """
    快速设置日志记录器的便捷函数

    参数:
        name: 日志记录器名称
        base_dir: 日志根目录
        level: 日志级别
        console_output: 是否同时输出到控制台

    返回:
        配置好的日志记录器

    示例:
        logger = setup_logger("MyApp", "logs", logging.INFO)
        logger.info("这是一条日志")
    """
    config = LoggerConfig(base_dir=base_dir, level=level, console_output=console_output)
    """日志配置对象"""
    return config.get_logger(name)
