"""程序启动模块

避免在导入包时立即导入 ``launcher.__main__``，以消除在
``python -m launcher`` 场景下的 RuntimeWarning。

外部若需要调用 ``launcher.main()``，我们提供一个惰性包装器，
仅在被调用时再导入 ``__main__`` 中的实现。
"""

from __future__ import annotations

__all__ = ["main"]


def main() -> None:
    # 惰性导入，避免在包导入阶段触发 __main__ 的加载
    from .__main__ import main as _main

    return _main()
