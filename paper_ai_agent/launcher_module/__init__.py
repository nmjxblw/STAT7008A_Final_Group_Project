"""程序启动模块

避免在导入包时立即导入 ``launcher.__main__``，以消除在
``python -m launcher`` 场景下的 RuntimeWarning。

外部若需要调用 ``launcher.run()``，我们提供一个惰性包装器，
仅在被调用时再导入 ``__main__`` 中的实现。
"""

from __future__ import annotations

__all__ = ["run"]


def run() -> None:
    """程序运行函数的惰性包装器"""
    from .__main__ import run as _run

    return _run()
