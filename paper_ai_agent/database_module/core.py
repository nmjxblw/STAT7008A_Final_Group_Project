"""数据库核心模块"""

from sqlalchemy.orm import sessionmaker, Session


_is_initialized = False
"""数据库初始化标志位"""


def _initialize_database() -> Session:
    """初始化数据库连接和会话"""
    global _is_initialized, session
    if _is_initialized:
        return session
    _is_initialized = True

    import logging
    import os
    from sqlalchemy import (
        Engine,
        create_engine,
        MetaData,
    )

    from global_module import DATABASE_PATH
    from log_module import logger

    _engine: Engine = create_engine(
        url=f"sqlite:///{DATABASE_PATH}",
        echo=True,
        # 连接池配置
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # 1小时回收
        pool_timeout=30,
        pool_pre_ping=True,
    )
    """数据库引擎实例"""

    # 将echo的日志重定向到自定义logger.handlers[0]
    _database_logger = logging.getLogger("sqlalchemy.engine")
    _database_logger.setLevel(logging.DEBUG)
    _database_logger.addHandler(logger.handlers[0])
    _database_logger.propagate = False  # 避免重复日志输出

    # region 创建数据库表和会话
    # 创建表,需在 File 类的定义之后执行
    try:
        if not os.path.exists(DATABASE_PATH):
            logger.debug(f"数据库文件不存在，输入路径: {DATABASE_PATH}")
            raise FileNotFoundError("数据库文件不存在！")
        if not str(DATABASE_PATH).strip().endswith(".db"):
            logger.debug(f"数据库路径格式错误，输入路径: {DATABASE_PATH}")
            raise ValueError(".env文件数据库格式错误，必须是以 .db 结尾的文件路径！")
        logger.debug(f"开始创建表，数据库路径: {DATABASE_PATH} ")
        from .models import _Base

        meta_data: MetaData = _Base.metadata
        meta_data.create_all(_engine, checkfirst=True)
        logger.debug("✔ 数据库表创建完成")
    except Exception as e:
        logger.debug(f"✘ 创建表失败: {e}")
        raise e

    # 创建会话
    try:
        logger.debug("正在创建数据库会话...")
        _Session = sessionmaker(bind=_engine)
        session = _Session()
        """ 数据库会话实例 """
        logger.debug("✔ 数据库会话创建成功")
    except Exception as e:
        logger.debug(f"✘ 创建数据库会话失败: {e}")
        raise e
    # endregion

    return session


session = _initialize_database()
"""数据库会话实例"""
