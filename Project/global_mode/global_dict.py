import threading
from typing import Any, Optional
from utility_mode.singleton_meta import SingletonMeta
import threading
from collections import UserDict


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
