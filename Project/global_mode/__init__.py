"""全局变量模块"""

from .global_dynamic_object import *

__all__ = [
    "GlobalDynamicObject",
    "globals",
    "ProjectName",
    "ProjectDescription",
    "ProjectAuthor",
    "system_config",
    "crawler_config",
    "logging_config",
    "answer_generator_config",
    "file_classifier_config",
]

# region 项目静态信息
ProjectName: str = "论文检索智能体"
"""项目名称"""
ProjectDescription: str = "PDF文档分析与知识检索系统"
"""项目描述"""
ProjectAuthor: str = "STAT7008A Group 19"
"""项目作者"""
# endregion
