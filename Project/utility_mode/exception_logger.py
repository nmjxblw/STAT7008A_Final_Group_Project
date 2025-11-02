"""
由DeepSeek生成的全局异常捕获记录器
在模块导入时自动初始化并开始捕获全局异常
"""

import logging
import sys
import threading
from datetime import datetime
import os
from types import TracebackType
from typing import Any, Callable, Optional, Self, Tuple, Type
import tkinter as tk
from tkinter import messagebox


class ExceptionLogger:
    """
    全局异常捕获记录器（模拟静态类行为）
    在模块导入时自动初始化并开始捕获全局异常
    """

    # 模块私有变量
    _instance: Self | None = None  # 异常捕获器实例化
    _lock: threading.Lock = threading.Lock()
    """线程锁
    """

    __initialized: bool = False
    """触发重写规则，防止外部意外修改初始化状态"""

    # 定义致命错误类型（可根据需要扩展）
    _FATAL_EXCEPTIONS = (
        SystemExit,
        KeyboardInterrupt,
        MemoryError,
        SystemError,
        RecursionError,
        ImportError,  # 如果模块导入失败可能导致程序无法运行
    )

    def __new__(cls):
        """
        创建单例实例化，确保只有一个异常捕获器实例存在并使用线程锁
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        """
        初始化异常捕获器实例，
        生成异常捕获日志文件和重写异常捕获钩子
        """
        if not ExceptionLogger.__initialized:
            with ExceptionLogger._lock:
                if not ExceptionLogger.__initialized:
                    self.setup_logging()
                    self.override_excepthook()
                    ExceptionLogger.__initialized = True

    def setup_logging(self) -> None:
        """配置日志记录"""
        # 创建日志目录
        log_dir = "logs/exceptions"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建按日期命名的日志文件
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(os.getcwd(), log_dir, f"{date_str}.log")

        # 配置logging
        logging.basicConfig(
            level=logging.ERROR | logging.INFO | logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stderr),  # 同时输出到控制台
            ],
        )

        # 初始化记录器
        self.logger = logging.getLogger("异常日志记录器")
        self.logger.info("全局异常记录器初始化完成")

    @classmethod
    def is_fatal_error(
        cls, exc_type: Type[BaseException], exc_value: BaseException
    ) -> bool:
        """
        判断异常是否为致命错误

        Args:
            exc_type: 异常类型
            exc_value: 异常值

        Returns:
            bool: 是否为致命错误
        """
        # 1. 检查异常类型是否在预定义致命错误列表中
        if issubclass(exc_type, cls._FATAL_EXCEPTIONS):
            return True

        # 2. 检查异常信息中是否包含致命关键词
        fatal_keywords = ["fatal", "critical", "memory", "system", "recursion"]
        error_msg = str(exc_value).lower()
        if any(keyword in error_msg for keyword in fatal_keywords):
            return True

        # 3. 可以根据具体业务逻辑添加更多判断条件
        # 例如：数据库连接失败、核心组件初始化失败等

        return False

    @classmethod
    def handle_exception(
        cls,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
    ) -> None:
        """
        统一异常处理方法，包含弹窗提示和智能错误判断

        Args:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常追踪信息
        """
        # 记录异常信息
        cls().logger.error(
            "未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback)
        )

        # 判断是否为致命错误
        is_fatal = cls.is_fatal_error(exc_type, exc_value)

        if is_fatal:
            cls().logger.critical("致命错误 detected, 程序将终止")
            # 致命错误直接退出
            sys.exit(1)
        else:
            # 非致命错误显示弹窗让用户选择
            cls.show_error_dialog(exc_type, exc_value, exc_traceback)

    @classmethod
    def show_error_dialog(
        cls,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
    ) -> None:
        """
        显示错误弹窗让用户选择继续运行或退出程序
        """
        # 获取异常详细信息
        error_type: str = exc_type.__name__
        error_msg: str = str(exc_value)
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口

            # 简化追踪信息（只取最后一行）
            if exc_traceback:
                tb_lines = []
                tb = exc_traceback
                while tb is not None:
                    frame = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = frame.f_code.co_filename
                    tb_lines.append(f"File {filename}, line {lineno}")
                    tb = tb.tb_next
                traceback_info = "\n".join(tb_lines[-3:])  # 只显示最后3行追踪
            else:
                traceback_info = "无追踪信息"

            # 显示警告框并获取用户选择
            result = messagebox.askquestion(
                "程序异常",
                f"程序发生异常：\n{error_type}: {error_msg}\n\n追踪信息：{traceback_info}\n\n请选择处理方式：",
                icon="warning",
                detail="选择'确定'继续运行程序（可能不稳定），选择'取消'退出程序",
            )

            root.destroy()

            # 处理用户选择
            if result == "cancel":  # 用户选择退出程序
                cls().logger.info("用户选择退出程序")
                sys.exit(1)
            else:  # 用户选择继续运行
                cls().logger.info("用户选择继续运行程序")

        except Exception as dialog_error:
            # 弹窗本身出错时的备选方案
            cls().logger.error("弹窗显示失败，使用控制台提示", exc_info=dialog_error)
            print(f"程序发生异常：{error_type}: {error_msg}")
            print("由于弹窗显示失败，程序将继续运行")

    def override_excepthook(self) -> None:
        """重写全局异常钩子"""
        original_excepthook: Callable[
            [Type[BaseException], BaseException, Optional[TracebackType]], Any
        ] = sys.excepthook

        def custom_excepthook(
            exc_type: Type[BaseException],
            exc_value: BaseException,
            exc_traceback: Optional[TracebackType],
        ) -> None:
            """
            自定义异常处理函数
            """
            # 忽略KeyboardInterrupt，让正常退出流程处理
            if issubclass(exc_type, KeyboardInterrupt):
                if original_excepthook is not None:
                    original_excepthook(exc_type, exc_value, exc_traceback)
                return

            # 使用统一的异常处理方法
            self.handle_exception(exc_type, exc_value, exc_traceback)

            # 调用原始excepthook以确保正常行为
            if original_excepthook is not None:
                original_excepthook(exc_type, exc_value, exc_traceback)

        # 设置自定义异常钩子
        sys.excepthook = custom_excepthook

    @classmethod
    def register_thread_exception_handler(cls) -> None:
        """
        注册线程异常处理（可选）
        用于捕获线程中的未处理异常
        """

        def thread_exception_handler(args: threading.ExceptHookArgs) -> None:
            """线程异常处理方法

            Args:
                args (threading.ExceptHookArgs): 异常处理钩子，包含异常的类型、异常的实例值、异常的追踪信息以及引发异常的线程对象的
            """
            # 处理可能的 None 值，确保类型安全
            exc_type: Type[BaseException] = args.exc_type
            # 如果 exc_value 为 None，创建一个默认的异常实例
            exc_value: BaseException = (
                args.exc_value if args.exc_value is not None else args.exc_type()
            )
            exc_traceback: Optional[TracebackType] = args.exc_traceback

            # 使用统一的异常处理方法
            cls.handle_exception(exc_type, exc_value, exc_traceback)

        # 设置线程异常处理
        threading.excepthook = thread_exception_handler

    @classmethod
    def manual_log_exception(
        cls, exception_instance: BaseException, fatal: bool = False
    ) -> None:
        """
        手动记录异常并弹出警告框，让用户选择继续运行或退出程序

        Args:
            exception_instance: 异常实例
            fatal: 是否为致命错误（致命错误将直接退出程序）
        """
        # 自动判断是否为致命错误（如果未手动指定）
        if not fatal:
            fatal = cls.is_fatal_error(type(exception_instance), exception_instance)

        # 记录异常到日志
        cls().logger.error("手动捕获的异常:", exc_info=exception_instance)

        # 如果是致命错误，直接退出程序
        if fatal:
            cls().logger.critical("遇到致命错误，程序即将退出")
            sys.exit(1)

        # 非致命错误显示弹窗
        cls.show_error_dialog(type(exception_instance), exception_instance, None)

    @classmethod
    def add_fatal_exception(cls, exception_type: Type[BaseException]) -> None:
        """
        添加自定义致命错误类型

        Args:
            exception_type: 要添加的致命错误类型
        """
        cls._FATAL_EXCEPTIONS += (exception_type,)


# 在模块导入时自动创建实例并初始化
_global_exception_logger = ExceptionLogger()

# 可选：注册线程异常处理
ExceptionLogger.register_thread_exception_handler()
