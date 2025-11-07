"""日志模块"""

import os
import sys
import logging
from types import FrameType, TracebackType
from typing import Optional, Tuple, Type
from global_module import PROJECT_NAME
from ._logger import setup_logger
import sys

__all__ = ["logger"]

# 全局默认日志记录器
logger: logging.Logger = setup_logger(name=PROJECT_NAME, level=logging.DEBUG)
"""全局默认日志记录器对象"""

# region 全局未捕获异常处理钩子

_exception_handler_initialized: bool = False
"""全局异常处理器初始化标志"""


def is_fatal_error(exc_type: Type[BaseException], exc_value: BaseException) -> bool:
    """判断异常是否为致命错误"""
    if issubclass(
        exc_type,
        (
            SystemExit,
            KeyboardInterrupt,
            MemoryError,
            SystemError,
            RecursionError,
            ImportError,
        ),
    ):
        return True

    fatal_keywords = ["fatal", "critical", "memory", "system", "recursion"]
    error_msg = str(exc_value).lower()
    if any(keyword in error_msg for keyword in fatal_keywords):
        return True

    return False


def _setup_custom_exception_hook():
    """设置自定义的全局异常钩子以记录未捕获的异常"""

    global _exception_handler_initialized
    # 判断初始化状态，确保只初始化一次
    if _exception_handler_initialized:
        return
    _exception_handler_initialized = True
    global logger

    def handle_exception(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: Optional[TracebackType],
    ):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 允许键盘中断正常退出
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        # 提取异常位置信息
        filename, lineno = _extract_exception_location(exc_traceback)

        # 记录异常信息
        logger.error(
            "\n捕获异常:[%s: %s] 在 [%s:%s]",
            exc_type.__name__,
            str(exc_value),
            filename,
            lineno,
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        if is_fatal_error(exc_type, exc_value):
            logger.critical("检测到致命错误，程序将终止。")
            sys.exit(1)

    sys.excepthook = handle_exception
    logger.debug("✔ 全局未捕获的异常处理钩子已设置。")


def _extract_exception_location(
    exc_traceback: Optional[TracebackType],
) -> Tuple[str, int]:
    """提取异常位置信息"""
    filename: str = "<unknown>"
    lineno: int = -1
    if exc_traceback is not None:
        last_tb: TracebackType = exc_traceback
        while last_tb.tb_next is not None:
            last_tb = last_tb.tb_next
        frame: FrameType = last_tb.tb_frame
        filename = os.path.basename(frame.f_code.co_filename)  # 只取文件名
        lineno = last_tb.tb_lineno
    return filename, lineno


_setup_custom_exception_hook()
# endregion
