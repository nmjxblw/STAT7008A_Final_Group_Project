import json
from os import PathLike
import threading
from typing import Any, Dict, Optional, Union
from utility_mode import SingletonMeta
from pathlib import Path
import pathlib


class GlobalDynamicObject(metaclass=SingletonMeta):
    """
    全局动态对象（单例 + 线程安全）

    功能：
    - 从 JSON 加载为动态对象（支持嵌套 dict/list）
    - 属性式增删改查（obj.key / obj.key = value / del obj.key）
    - 字典式/下标式访问（obj['key'] / obj[0]）
    - 单例（全局唯一实例），适合作为全局配置或状态容器
    - 线程安全（使用可重入锁 RLock，全树共享）
    - 支持保存为 JSON、更新、转换为 dict/JSON 字符串

    注意：
    - 仅顶层为单例；内部节点使用内部类 Node 表示，不是单例。
    - 未找到的属性将返回 None（与历史实现保持一致）。
    """

    # ============= 内部节点类型（非单例） =============
    class _Node:
        """表示动态对象的节点（支持 dict/list/标量）。"""

        def __init__(self, data: Any = None, lock: Optional[threading.RLock] = None):
            # 内部保留属性使用前导下划线，避免与业务键冲突
            self._lock: threading.RLock = lock or threading.RLock()
            self._data: Dict[str, Any] = {}
            self._items: Optional[list] = None  # 仅当表示 list 时生效
            if data is not None:
                self._build_from_data(data)

        # ---------- 构建 ----------
        def _build_from_data(self, data: Any) -> None:
            """从原始数据构建节点内容。"""
            with self._lock:
                if isinstance(data, dict):
                    self._items = None
                    for k, v in data.items():
                        self._data[k] = self._wrap(v)
                elif isinstance(data, list):
                    self._data.clear()
                    self._items = [self._wrap(v) for v in data]
                else:
                    # 标量类型：作为单键值节点保存到 _data['value']
                    self._items = None
                    self._data["value"] = data

        def _wrap(self, v: Any) -> Any:
            """将值包装为节点（若为 dict/list）。"""
            if isinstance(v, (dict, list)):
                return GlobalDynamicObject._Node(v, self._lock)
            return v

        def _unwrap(self, v: Any) -> Any:
            """将节点解包为原始数据（递归）。"""
            if isinstance(v, GlobalDynamicObject._Node):
                return v.to_dict()
            return v

        # ---------- 属性访问 ----------
        def __getattr__(self, name: str) -> Any:
            """获取属性值"""
            # 未找到属性时返回 None（与历史实现保持一致）
            if name.startswith("_"):
                raise AttributeError(f"'{type(self).__name__}'对象没有属性'{name}'")
            with self._lock:
                if self._items is not None:
                    # list 节点支持 node.0 / node.1 的访问（可读性用途）
                    try:
                        idx = int(name)
                        if 0 <= idx < len(self._items):
                            return self._items[idx]
                    except ValueError:
                        pass
                    return None
                return self._data.get(name, None)

        def __setattr__(self, name: str, value: Any) -> None:
            """设置属性值"""
            if name in {"_lock", "_data", "_items"}:
                return super().__setattr__(name, value)
            with self._lock:
                if self._items is not None:
                    # list 节点不支持通过属性名设置元素
                    raise TypeError("列表节点不支持属性赋值，请使用索引或替换整个列表")
                self._data[name] = self._wrap(value)

        def __delattr__(self, name: str) -> None:
            """删除属性值"""
            if name in {"_lock", "_data", "_items"}:
                raise AttributeError(f"不可删除内部属性: {name}")
            with self._lock:
                if self._items is not None:
                    raise TypeError("列表节点不支持通过属性名删除元素")
                if name in self._data:
                    del self._data[name]
                else:
                    # 与 __getattr__ 行为一致，静默处理
                    pass

        # ---------- 下标访问 ----------
        def __getitem__(self, key: Union[str, int]) -> Any:
            """获取下标元素"""
            with self._lock:
                if isinstance(key, int):
                    if self._items is None:
                        raise TypeError("此节点不是列表，无法使用整数索引")
                    return self._items[key]
                else:
                    if self._items is not None:
                        raise TypeError("此节点是列表，无法使用字符串键")
                    return self._data[key]

        def __setitem__(self, key: Union[str, int], value: Any) -> None:
            """设置下标元素"""
            with self._lock:
                if isinstance(key, int):
                    if self._items is None:
                        raise TypeError("此节点不是列表，无法使用整数索引")
                    self._items[key] = self._wrap(value)
                else:
                    if self._items is not None:
                        raise TypeError("此节点是列表，无法使用字符串键")
                    self._data[key] = self._wrap(value)

        # ---------- 工具方法 ----------
        def get(self, key: str, default: Any = None) -> Any:
            """获取键对应的值，若不存在则返回默认值"""
            with self._lock:
                if self._items is not None:
                    try:
                        idx = int(key)
                        return self._items[idx]
                    except Exception:
                        return default
                return self._data.get(key, default)

        def update(self, new_data: Dict[str, Any]) -> None:
            """更新节点内容（支持递归）。"""
            with self._lock:
                if self._items is not None:
                    raise TypeError("列表节点不支持字典式更新")
                for k, v in new_data.items():
                    self._data[k] = self._wrap(v)

        def to_dict(self) -> Any:
            """将节点及其子节点递归转换为原始数据结构（dict/list/标量）。"""
            with self._lock:
                if self._items is not None:
                    return [self._unwrap(v) for v in self._items]
                result: Dict[str, Any] = {}
                for k, v in self._data.items():
                    result[k] = self._unwrap(v)
                return result

    # ============= 顶层单例对象 =============
    def __init__(self, data: Any = None):
        # 顶层可重入锁，供全树共享
        if not hasattr(self, "_initialized"):
            self._lock = threading.RLock()
            self._root = GlobalDynamicObject._Node({}, self._lock)
            self._file_path: Optional[
                int | str | bytes | PathLike[str] | PathLike[bytes]
            ] = None
            self._initialized = True
            print("全局变量初始化成功。")
        if data is not None:
            self.load_from_data(data)

    # ---------- 构建 / 加载 / 保存 ----------
    def load(
        self, file_path: int | str | bytes | PathLike[str] | PathLike[bytes]
    ) -> None:
        """从 JSON 文件加载为动态对象（覆盖当前内容）。"""
        with self._lock:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._root = GlobalDynamicObject._Node(data, self._lock)
            self._file_path = file_path

    def load_from_data(self, data: Any) -> None:
        """从已有数据构建（覆盖当前内容）。"""
        with self._lock:
            self._root = GlobalDynamicObject._Node(data, self._lock)

    def save(
        self,
        file_path: Optional[int | str | bytes | PathLike[str] | PathLike[bytes]] = None,
    ) -> None:
        """保存当前对象到 JSON 文件。若未指定路径，使用最近一次 load 的路径。"""
        with self._lock:
            target: Optional[Union[int, str, bytes, PathLike[str], PathLike[bytes]]] = (
                file_path or self._file_path
            )
            if not target:
                raise ValueError("未指定保存路径")
            with open(target, "w", encoding="utf-8") as f:
                json.dump(self._root.to_dict(), f, ensure_ascii=False, indent=2)

    # ---------- 顶层属性/下标访问委托给 _root ----------
    def __getattr__(self, name: str) -> Any:
        """获取属性值"""
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}'对象没有属性'{name}'")
        with self._lock:
            return getattr(self._root, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """设置属性值"""
        if name in {"_lock", "_root", "_file_path", "_initialized"}:
            return super().__setattr__(name, value)
        with self._lock:
            setattr(self._root, name, value)

    def __delattr__(self, name: str) -> None:
        """删除属性值"""
        if name in {"_lock", "_root", "_file_path", "_initialized"}:
            raise AttributeError(f"不可删除内部属性: {name}")
        with self._lock:
            delattr(self._root, name)

    def __getitem__(self, key: Union[str, int]) -> Any:
        """获取下标元素"""
        with self._lock:
            return self._root[key]

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """设置下标元素"""
        with self._lock:
            self._root[key] = value

    # ---------- 工具方法 ----------
    def get(self, key: str, default: Any = None) -> Any:
        """获取键对应的值，若不存在则返回默认值"""
        with self._lock:
            return self._root.get(key, default)

    def update(self, new_data: Dict[str, Any]) -> None:
        """更新顶层内容（支持递归）。"""
        with self._lock:
            self._root.update(new_data)

    def hasattr(self, name: str) -> bool:
        """检查顶层是否存在指定名称的键（不依赖内置 hasattr 语义）。

        注意：与 Python 内置 hasattr 不同，本方法不会因为 __getattr__ 返回 None 而误判，
        仅在键真实存在于顶层字典时返回 True。
        """
        with self._lock:
            node = self._root
            # 仅当为 dict 节点时才有键集合
            if node._items is not None:
                return False
            return name in node._data

    def to_dict(self) -> Any:
        """将整个对象递归转换为原始数据结构（dict/list/标量）。"""
        with self._lock:
            return self._root.to_dict()

    def to_json(self, indent: Optional[int] = None) -> str:
        """将整个对象递归转换为 JSON 字符串。"""
        with self._lock:
            return json.dumps(self._root.to_dict(), ensure_ascii=False, indent=indent)


globals: GlobalDynamicObject = GlobalDynamicObject()
"""全局变量实例（单例）"""
try:
    globals.load(Path.joinpath(Path.cwd(), "app_settings.json"))
except Exception:
    raise RuntimeError(
        "初始化全局变量时发生错误，请检查 app_settings.json 文件格式是否正确。"
    )


def _load_config_or_raise_error(
    config_name: str, error_message: str
) -> GlobalDynamicObject._Node:
    """获取指定名称的全局配置对象，若不存在则抛出错误。"""
    global globals
    if globals is None:
        raise RuntimeError("初始化全局变量时发生错误，globals 为 None。")
    if globals.hasattr(config_name) and getattr(globals, config_name):
        return getattr(globals, config_name)
    else:
        raise RuntimeError(error_message)


system_config: GlobalDynamicObject._Node = _load_config_or_raise_error(
    "system_config", "系统模式配置未找到或未正确加载。"
)
"""全局系统模式配置对象"""
crawler_config: GlobalDynamicObject._Node = _load_config_or_raise_error(
    "crawler_config", "爬虫配置未找到或未正确加载。"
)
"""全局爬虫配置对象"""
logging_config: GlobalDynamicObject._Node = _load_config_or_raise_error(
    "logging_config", "日志配置未找到或未正确加载。"
)
"""全局日志配置对象"""
answer_generator_config: GlobalDynamicObject._Node = _load_config_or_raise_error(
    "answer_generator_config", "回答生成器配置未找到或未正确加载。"
)
"""全局回答生成器配置对象"""
file_classifier_config: GlobalDynamicObject._Node = _load_config_or_raise_error(
    "file_classifier_config", "文件分类器配置未找到或未正确加载。"
)
"""全局文件分类器配置对象"""
