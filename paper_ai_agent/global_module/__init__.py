"""全局变量模块"""

from .global_dynamic_object import *

__all__ = [
    "GlobalDynamicObject",
    "globals",
    "ProjectName",
    "ProjectDescription",
    "ProjectAuthor",
    "DatabasePath",
    "system_config",
    "crawler_config",
    "answer_generator_config",
    "file_classifier_config",
]

# region 项目静态信息
ProjectName: str = system_config.get("project_name", "PDF文档分析与知识检索系统")
"""项目名称"""
ProjectDescription: str = system_config.get(
    "project_description", "PDF文档分析与知识检索系统"
)
"""项目描述"""
ProjectAuthor: str = system_config.get("project_author", "STAT7008A Group 19")
"""项目作者"""
DatabasePath: str = system_config.get("database_path", "DB/app_database.db")
"""数据库路径"""
# endregion
