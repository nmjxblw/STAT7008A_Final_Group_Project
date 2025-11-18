"""文档归档智能体模块

对外接口：
    - start_file_classify_task: 启动文件分类任务
    - run: 运行默认配置的分类任务
    - test_retrieval: 测试检索功能
    - get_retrieval_content: RAG综合检索（供其他模块调用）
    - get_local_embedding_model: 获取本地embedding模型
"""

from .__main__ import *

from .utils import *

__all__ = [
    "start_file_classify_task",
    "stop_file_classify_task",
    "pause_file_classify_task",
    "resume_file_classify_task",
    "run",
    "test_retrieval",
    "get_retrieval_content",
    "get_local_embedding_model",
]
