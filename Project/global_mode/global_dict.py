import threading
from typing import Any, Optional
from utility_mode import SingletonMeta
import threading
from collections import UserDict
from pathlib import Path
import json


class GlobalDict(UserDict, metaclass=SingletonMeta):
    """线程安全的全局字典类，用于存储全局变量。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def __setitem__(self, key: Any, value: Any):
        with self.lock:
            super().__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        with self.lock:
            return super().__getitem__(key)

    def __delitem__(self, key: Any):
        with self.lock:
            super().__delitem__(key)

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        with self.lock:
            return super().get(key, default)

    def set(self, key: Any, value: Any):
        with self.lock:
            super().__setitem__(key, value)

    def delete(self, key: Any):
        with self.lock:
            super().__delitem__(key)

    def remove(self, key: Any):
        """删除指定键及其对应的值。"""
        with self.lock:
            if key in self.data:
                super().__delitem__(key)

    def clear(self):
        """清空所有全局变量。"""
        with self.lock:
            super().clear()


globals = GlobalDict()
"""线程安全的全局字典，用于存储全局变量。"""


def _create_global_dict(
    file_path: Path = Path.joinpath(Path.cwd(), "app_settings.json")
) -> GlobalDict:
    """创建并返回全局字典实例。"""
    global_dict = GlobalDict()
    if file_path.exists():
        try:

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                with global_dict.lock:
                    for key, value in data.items():
                        global_dict[key] = value
        except Exception as e:
            print(f"加载全局字典时发生错误: {e}")
    return global_dict


def get_global(key: Any) -> Any:
    r"""获取全局变量。

    Args:
        key (Any): 配置节名称。例如：crawling_mode_config
    """
    with globals.lock:
        return globals.get(key, {}).copy()


def set_global(key: Any, *keys: Any, value: Optional[Any] = None) -> bool:
    r"""
    设置全局变量。

    Args:
        key (Any): 配置节名称。例如：crawling_mode_config
        *keys (Any): 其他配置节名称。
        value (Optional[Any]): 要设置的值。

    Example:
        set_global("crawling_mode_config", "timeout", value=30)

    Returns:
        bool: 设置是否成功。
    """
    with globals.lock:
        try:
            if not keys:
                globals[key] = value
            else:
                current_level: dict[str, Any] = globals.setdefault(key, {})
                for k in keys[:-1]:
                    current_level = current_level.setdefault(k, {})
                current_level[keys[-1]] = value
            return True
        except Exception as e:
            print(f"设置全局变量失败: {e}")
            return False
