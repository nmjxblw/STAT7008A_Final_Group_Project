"""文档归档智能体模块

对外接口：
    同步接口（旧接口，保持兼容）：
        - start_file_classify_task: 启动文件分类任务（同步阻塞）
        - run: 运行默认配置的分类任务
        - test_retrieval: 测试检索功能
    
    异步接口（推荐使用，解决线程生命周期问题）：
        - add_classify_task: 添加文档归类任务到队列（立即返回，后台处理）
        - get_queue_status: 获取任务队列状态
        - start_queue_worker: 启动队列工作线程（通常不需要手动调用）
        - stop_queue_worker: 停止队列工作线程（程序退出时调用）
    
    RAG检索接口：
        - get_retrieval_content: RAG综合检索（供其他模块调用）
    
    工具接口：
        - get_local_embedding_model: 获取本地embedding模型（单例）

使用示例（爬虫模块推荐用法）：
    >>> from file_classifier_module import add_classify_task, get_queue_status
    >>> 
    >>> # 爬取到新文件后，添加到归类队列
    >>> success = add_classify_task("/path/to/unclassified/paper.pdf")
    >>> if success:
    >>>     print("任务已加入队列，爬虫可以继续工作")
    >>> 
    >>> # 查询队列状态
    >>> status = get_queue_status()
    >>> print(f"队列中有 {status['queue_size']} 个任务等待处理")
"""

from .__main__ import start_file_classify_task, run, test_retrieval
from .utils import get_retrieval_content, get_local_embedding_model
from .task_queue import (
    add_classify_task,
    get_queue_status,
    start_queue_worker,
    stop_queue_worker
)

__all__ = [
    # 同步接口
    "start_file_classify_task",
    "run",
    "test_retrieval",
    
    # 异步接口（推荐）
    "add_classify_task",
    "get_queue_status",
    "start_queue_worker",
    "stop_queue_worker",
    
    # RAG检索接口
    "get_retrieval_content",
    
    # 工具接口
    "get_local_embedding_model"
]
