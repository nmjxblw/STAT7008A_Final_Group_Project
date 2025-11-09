import os
import shutil
from datetime import datetime
import hashlib
from log_module import logger


class FileHandler:
    """文件处理类，负责文件保存"""

    def __init__(self, base_path="./Resources"):
        self.base_path = base_path
        self.create_directories()

    def create_directories(self):
        """创建必要的目录结构"""
        directories = [
            f"{self.base_path}/Unclassified",
            f"{self.base_path}/Unclassified/PDF",
            f"{self.base_path}/Unclassified/PNG",
            f"{self.base_path}/Unclassified/JPG",
            f"{self.base_path}/Unclassified/TXT",
            "Crawling Log",
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def save_file(self, content, url, file_type):
        """保存文件到分类目录"""
        # 生成唯一文件名
        file_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_extension = file_type.lower()

        # 确定文件类型目录
        type_folders = {".pdf": "PDF", ".txt": "TXT", ".jpg": "JPG", ".png": "PNG"}
        folder = type_folders.get(file_type, "Other")

        filename = f"{timestamp}_{file_hash}{file_extension}"
        filepath = f"{self.base_path}/Unclassified/{folder}/{filename}"

        try:
            with open(filepath, "wb") as f:
                f.write(content)

            # 记录到日志
            self.log_download(url, filepath)
            return filepath
        except Exception as e:
            logger.error(f" 文件保存失败: {e}")
            return None

    def log_download(self, url, filepath):
        """记录下载日志"""
        log_dir = "Crawling Log"
        log_file = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"

        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] FileName:\"{os.path.basename(filepath)}\" Url:\"{url}\"\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
