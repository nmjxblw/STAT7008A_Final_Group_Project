from utility_mode import SingletonMeta
from log_module import logger


class DBHandler(metaclass=SingletonMeta):
    """数据库处理类"""

    def __init__(self):
        self.connection = None
        logger.debug("数据库处理类实例化完成")

    def connect(self, connection_string):
        """连接到数据库"""
        # 这里添加连接数据库的逻辑
        self.connection = f"Connected to {connection_string}"

    def disconnect(self):
        """断开数据库连接"""
        # 这里添加断开数据库连接的逻辑
        self.connection = None
