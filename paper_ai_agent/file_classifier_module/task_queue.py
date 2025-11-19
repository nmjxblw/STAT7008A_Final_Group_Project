"""文档归类异步任务队列

解决问题：
    当爬虫模块在内置线程中调用文档归类接口时，如果爬虫主线程被销毁，
    归类线程也会自动销毁，导致归类任务做不完。

解决方案：
    使用消息队列机制，爬虫模块将任务添加到队列后立即返回，
    文档归类模块在后台独立线程中持续处理队列中的任务。
    即使爬虫线程销毁，归类线程也会继续工作直到所有任务完成。

使用方式：
    # 在程序启动时（可选，会自动启动）
    start_queue_worker()
    
    # 爬虫模块添加任务
    add_classify_task("/path/to/unclassified/file.pdf")
    
    # 查询队列状态
    status = get_queue_status()
    
    # 程序退出前（可选，会自动停止）
    stop_queue_worker()
"""

import queue
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from log_module import logger
from utility_module import SingletonMeta


class TaskQueueManager(metaclass=SingletonMeta):
    """文档归类任务队列管理器（单例模式）"""
    
    def __init__(self):
        """初始化任务队列管理器"""
        self._task_queue: queue.Queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False
        self._lock = threading.Lock()
        
        # 统计信息
        self._total_tasks = 0
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._current_task: Optional[str] = None
        
        logger.debug("TaskQueueManager单例已创建")
    
    def start_worker(self):
        """启动后台工作线程"""
        with self._lock:
            if self._is_running:
                logger.warning("任务队列工作线程已在运行，无需重复启动")
                return
            
            self._stop_event.clear()
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                name="FileClassifierWorker",
                daemon=False  # 不使用daemon，确保任务完成
            )
            self._worker_thread.start()
            self._is_running = True
            logger.info("文档归类任务队列工作线程已启动")
    
    def stop_worker(self, timeout: float = 30.0):
        """
        停止后台工作线程（优雅停止）
        
        Args:
            timeout: 等待线程结束的超时时间（秒）
        """
        with self._lock:
            if not self._is_running:
                logger.debug("任务队列工作线程未运行，无需停止")
                return
            
            logger.info("正在停止文档归类任务队列工作线程...")
            self._stop_event.set()
        
        # 在锁外等待线程结束
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=timeout)
            if self._worker_thread.is_alive():
                logger.warning(f"工作线程在{timeout}秒后仍未结束，可能有任务正在处理")
            else:
                logger.info("文档归类任务队列工作线程已停止")
        
        with self._lock:
            self._is_running = False
    
    def add_task(self, file_path: str) -> bool:
        """
        添加文档归类任务到队列
        
        Args:
            file_path: 待归类文件的完整路径
            
        Returns:
            bool: 是否成功添加到队列
        """
        try:
            # 验证文件路径
            path = Path(file_path)
            if not path.exists():
                logger.error(f"添加任务失败：文件不存在 - {file_path}")
                return False
            
            if not path.is_file():
                logger.error(f"添加任务失败：路径不是文件 - {file_path}")
                return False
            
            # 检查文件类型
            if path.suffix.lower() != '.pdf':
                logger.error(f"添加任务失败：当前只支持PDF文件 - {file_path}")
                return False
            
            # 自动启动工作线程（如果未启动）
            if not self._is_running:
                logger.info("检测到首个任务，自动启动工作线程")
                self.start_worker()
            
            # 添加到队列
            self._task_queue.put(file_path)
            self._total_tasks += 1
            
            logger.info(f"任务已添加到队列：{path.name}（队列长度：{self._task_queue.qsize()}）")
            return True
            
        except Exception as e:
            logger.error(f"添加任务失败：{e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取队列状态信息
        
        Returns:
            dict: 包含队列状态的字典
        """
        return {
            "is_running": self._is_running,
            "queue_size": self._task_queue.qsize(),
            "total_tasks": self._total_tasks,
            "completed_tasks": self._completed_tasks,
            "failed_tasks": self._failed_tasks,
            "current_task": self._current_task,
            "pending_tasks": self._total_tasks - self._completed_tasks - self._failed_tasks
        }
    
    def _worker_loop(self):
        """后台工作线程的主循环"""
        logger.info("文档归类工作线程开始运行")
        
        while not self._stop_event.is_set():
            try:
                # 从队列获取任务（超时1秒，避免阻塞停止信号）
                try:
                    file_path = self._task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 处理任务
                self._current_task = file_path
                logger.info(f"开始处理任务：{Path(file_path).name}")
                
                try:
                    self._process_task(file_path)
                    self._completed_tasks += 1
                    logger.info(f"任务处理成功：{Path(file_path).name}（已完成：{self._completed_tasks}/{self._total_tasks}）")
                except Exception as e:
                    self._failed_tasks += 1
                    logger.error(f"任务处理失败：{Path(file_path).name} - {e}")
                finally:
                    self._current_task = None
                    self._task_queue.task_done()
                
            except Exception as e:
                logger.error(f"工作线程异常：{e}")
                time.sleep(1)  # 避免异常循环
        
        # 处理剩余任务
        remaining = self._task_queue.qsize()
        if remaining > 0:
            logger.info(f"工作线程停止信号收到，还有{remaining}个任务待处理，继续完成...")
            while not self._task_queue.empty():
                try:
                    file_path = self._task_queue.get_nowait()
                    self._current_task = file_path
                    logger.info(f"处理剩余任务：{Path(file_path).name}")
                    
                    try:
                        self._process_task(file_path)
                        self._completed_tasks += 1
                        logger.info(f"剩余任务处理成功：{Path(file_path).name}")
                    except Exception as e:
                        self._failed_tasks += 1
                        logger.error(f"剩余任务处理失败：{Path(file_path).name} - {e}")
                    finally:
                        self._current_task = None
                        self._task_queue.task_done()
                        
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"处理剩余任务异常：{e}")
        
        logger.info("文档归类工作线程已退出")
    
    def _process_task(self, file_path: str):
        """
        处理单个归类任务
        
        Args:
            file_path: 文件完整路径
        """
        from .__main__ import start_file_classify_task
        from global_module import file_classifier_config
        
        path = Path(file_path)
        
        # 获取配置
        config = file_classifier_config
        unclassified_dir = config.get("unclassified_dir", "")
        classified_dir = config.get("classified_dir", "")
        
        # 如果文件不在未分类目录下，使用文件所在目录
        if not unclassified_dir or str(path.parent) != unclassified_dir:
            unclassified_dir = str(path.parent)
        
        # 调用归类任务
        start_file_classify_task(
            unclassified_path=unclassified_dir,
            classified_path=classified_dir,
            file_type="pdf",
            file_name=path.name
        )


# 全局单例实例
_queue_manager = None


def _get_queue_manager() -> TaskQueueManager:
    """获取全局队列管理器实例"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = TaskQueueManager()
    return _queue_manager


# ========== 对外接口 ==========

def add_classify_task(file_path: str) -> bool:
    """
    添加文档归类任务到队列（异步）
    
    这是供爬虫模块调用的主要接口。爬虫模块调用此函数后立即返回，
    文档归类工作将在后台独立线程中进行，不受爬虫线程生命周期影响。
    
    Args:
        file_path: 待归类文件的完整路径（支持str或Path）
        
    Returns:
        bool: 是否成功添加到队列
        
    Example:
        >>> from file_classifier_module import add_classify_task
        >>> # 爬虫爬取到新文件后
        >>> success = add_classify_task("/path/to/unclassified/paper.pdf")
        >>> if success:
        >>>     print("任务已加入队列")
    """
    manager = _get_queue_manager()
    return manager.add_task(str(file_path))


def get_queue_status() -> Dict[str, Any]:
    """
    获取任务队列状态
    
    Returns:
        dict: 包含以下字段的状态字典：
            - is_running: 工作线程是否在运行
            - queue_size: 队列中待处理的任务数
            - total_tasks: 总任务数
            - completed_tasks: 已完成任务数
            - failed_tasks: 失败任务数
            - current_task: 当前正在处理的任务（文件路径）
            - pending_tasks: 待处理任务数
            
    Example:
        >>> from file_classifier_module import get_queue_status
        >>> status = get_queue_status()
        >>> print(f"队列中有 {status['queue_size']} 个任务等待处理")
        >>> print(f"已完成 {status['completed_tasks']}/{status['total_tasks']} 个任务")
    """
    manager = _get_queue_manager()
    return manager.get_status()


def start_queue_worker():
    """
    启动任务队列工作线程
    
    注意：通常不需要手动调用，首次add_classify_task时会自动启动。
    如果需要提前启动（例如预热），可以手动调用此函数。
    """
    manager = _get_queue_manager()
    manager.start_worker()


def stop_queue_worker(timeout: float = 30.0):
    """
    停止任务队列工作线程（优雅停止）
    
    会等待当前任务完成并处理队列中的剩余任务。
    
    Args:
        timeout: 等待超时时间（秒）
        
    注意：程序退出时建议调用此函数，确保所有任务处理完成。
    """
    manager = _get_queue_manager()
    manager.stop_worker(timeout=timeout)

