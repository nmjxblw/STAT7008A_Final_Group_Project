from enum import Enum, auto
from typing import Any

class DemandType(Enum):
    FILE_QUERY = auto()
    QA = auto()

def query_files_by_attributes(attributes: dict[str, Any]) -> list[dict[str, Any]]:
    """
    根据指定属性查询文件记录

    参数:
        attributes (dict[str, Any]): 包含查询属性的字典
    返回:
        files (list[dict[str, Any]]): 符合条件的文件列表（字典对象）
    """
    from database_module import query_files_by_attributes
    return query_files_by_attributes(attributes)
