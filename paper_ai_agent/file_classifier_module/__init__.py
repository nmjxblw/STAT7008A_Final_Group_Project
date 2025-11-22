"""文档归档智能体模块

========================================
接口说明
========================================

一、文档归类接口（文件处理）

1. 同步接口（旧接口，保持兼容）：
   - start_file_classify_task: 
     功能：启动文件分类任务，同步阻塞执行
     用途：直接处理单个PDF文件，包括文本提取、AI分析、RAG索引、数据库存储、文件移动
     特点：调用后会阻塞直到任务完成，适合单文件处理或不需要异步的场景
   
   - run:
     功能：运行默认配置的分类任务
     用途：批量处理未分类目录下的所有PDF文件
     特点：使用默认配置，自动扫描未分类目录并处理所有PDF文件

   - test_retrieval:
     功能：测试检索功能
     用途：用于测试RAG检索（FAISS和BM25）是否正常工作
     特点：开发调试用接口

2. 异步接口（推荐使用，解决线程生命周期问题）：
   - add_classify_task:
     功能：添加文档归类任务到异步队列，立即返回不阻塞
     用途：将PDF文件归类任务添加到后台队列，由独立工作线程处理
     特点：调用后立即返回，不阻塞调用线程；适合爬虫模块等需要异步处理的场景
     优势：即使调用线程销毁，归类任务也会在后台继续完成
   
   - get_queue_status:
     功能：获取任务队列的当前状态信息
     用途：查询队列中待处理任务数、已完成任务数、失败任务数、当前处理任务等
     特点：实时查询，不阻塞；返回字典包含队列的完整状态信息
   
   - start_queue_worker:
     功能：手动启动队列工作线程
     用途：提前启动后台工作线程（预热）
     特点：通常不需要手动调用，首次调用add_classify_task时会自动启动
   
   - pause_queue_worker:
     功能：暂停队列工作线程
     用途：临时暂停任务处理，当前任务会继续完成
     特点：暂停后新任务不会处理，但已添加的任务不会丢失，恢复后会继续处理
   
   - resume_queue_worker:
     功能：恢复队列工作线程
     用途：恢复暂停的任务处理
     特点：恢复后会继续处理队列中的任务
   
   - stop_queue_worker:
     功能：优雅停止队列工作线程
     用途：程序退出前确保所有任务处理完成
     特点：会等待当前任务完成并处理完队列中的剩余任务，不丢失任何任务

二、RAG检索接口（内容检索）

   - get_retrieval_content:
     功能：RAG综合检索，基于查询内容检索相关文档片段
     用途：根据用户查询，从已分类的文档中检索最相关的内容
     特点：结合FAISS向量检索和BM25关键词检索，返回综合排序结果
     返回：包含文档片段、相似度分数、来源文件等信息的列表

三、工具接口（模型和工具）

   - get_local_embedding_model:
     功能：获取本地embedding模型实例（单例模式）
     用途：获取用于向量化的embedding模型，供其他模块使用
     特点：单例模式，确保整个程序生命周期只加载一次模型，节省内存和时间


========================================
模块调用说明
========================================

一、Answer模块如何调用（RAG检索场景）

Answer模块需要根据用户问题检索相关文档内容时，应调用：
   - get_retrieval_content接口
   
调用流程：
   1. Answer模块接收用户问题/查询
   2. 调用get_retrieval_content，传入查询文本和检索数量
   3. 获取检索结果（相关文档片段列表）
   4. 基于检索结果生成答案

注意事项：
   - 此接口是同步接口，会立即返回检索结果
   - 检索结果已按相关度排序，可直接使用
   - 返回结果包含文档片段、相似度分数、来源文件等信息


二、异步场景如何调用（爬虫模块等）

当需要在异步环境中调用文档归类功能时（如爬虫模块），应使用异步接口：
   - add_classify_task接口（主要接口）
   - get_queue_status接口（可选，用于监控进度）

调用流程：
   1. 获取待归类PDF文件的完整路径
   2. 调用add_classify_task，传入文件路径
   3. 函数立即返回，不阻塞调用线程
   4. 后台独立工作线程自动处理归类任务
   5. （可选）调用get_queue_status查询处理进度

适用场景：
   - 爬虫模块：爬取到PDF后立即添加到队列，继续爬取下一篇
   - 批量处理：一次性添加多个文件到队列，后台依次处理
   - 多线程环境：避免线程生命周期问题，确保任务完成

注意事项：
   - add_classify_task是异步非阻塞接口，调用后立即返回
   - 归类任务在后台独立线程中执行，不受调用线程生命周期影响
   - 即使调用线程销毁，归类任务也会继续完成
   - 首次调用add_classify_task时会自动启动后台工作线程
   - 可通过get_queue_status实时查询任务处理状态


三、同步场景如何调用（直接处理）

当需要同步阻塞式处理文件时，应使用同步接口：
   - start_file_classify_task接口

调用流程：
   1. 准备未分类目录路径、已分类目录路径、文件类型、文件名
   2. 调用start_file_classify_task，传入上述参数
   3. 函数阻塞执行，直到任务完成
   4. 任务完成后函数返回

适用场景：
   - 单文件处理：需要等待处理结果后再继续
   - 命令行工具：需要同步执行并显示结果
   - 简单脚本：不需要异步处理的场景

注意事项：
   - 此接口是同步阻塞接口，会等待任务完成
   - 处理时间取决于PDF大小和复杂度（通常10-60秒）
   - 不适合在需要快速响应的线程中使用
"""

from pathlib import Path

from log_module import logger
from global_module import DATABASE_PATH

from .__main__ import start_file_classify_task, run, test_retrieval
from .corpus_singleton import CorpusSingleton
from .faiss_singleton import FAISSVectorStoreSingleton
from .utils import (
    get_retrieval_content,
    get_local_embedding_model,
    EmbeddingModelSingleton,
)
from .task_queue import (
    add_classify_task,
    get_queue_status,
    start_queue_worker,
    pause_queue_worker,
    resume_queue_worker,
    stop_queue_worker,
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
    "pause_queue_worker",
    "resume_queue_worker",
    "stop_queue_worker",
    
    # RAG检索接口
    "get_retrieval_content",
    
    # 工具接口
    "get_local_embedding_model"
]


# ========================================
# 模块级单例预加载（确保启动阶段完成初始化）
# ========================================
_embedding_model_instance = None

try:
    _embedding_model_instance = EmbeddingModelSingleton().get_model()
    if _embedding_model_instance is None:
        logger.warning("Embedding模型预加载失败，后续调用时将按需重试加载")
    else:
        logger.info("Embedding模型已在模块导入阶段完成预加载")
except Exception as exc:
    logger.error(f"模块导入阶段预加载Embedding模型失败：{exc}")

# 预初始化FAISS向量库（依赖embedding模型）
if _embedding_model_instance is not None:
    try:
        db_parent = Path(DATABASE_PATH).parent
        embedding_dir = db_parent / "embedding"
        FAISSVectorStoreSingleton(_embedding_model_instance, str(embedding_dir))
        logger.info("FAISS向量库单例已在模块导入阶段创建")
    except Exception as exc:
        logger.error(f"FAISS向量库预初始化失败：{exc}")
else:
    logger.warning("Embedding模型未就绪，跳过FAISS向量库预初始化")

# 预初始化BM25语料库
try:
    CorpusSingleton()
    logger.info("BM25语料库单例已在模块导入阶段创建")
except Exception as exc:
    logger.error(f"BM25语料库预初始化失败：{exc}")
