"""语义搜索与问答服务包"""

from __future__ import annotations

__all__ = [
    "generator",
]
from .answer_generator import Generator

generator = Generator()
""" 回答生成器实例 """
