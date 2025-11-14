from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


from datetime import datetime
# Document data model
@dataclass
class Document:
    """Internal representation of a document in your KB."""
    file_id: str
    title: str
    summary: str = ""
    content: str = ""
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    download_date: Optional[datetime] = None
    total_tokens: int = 0
    unique_tokens: int = 0
    text_length: int = 0

# 需求类型枚举
class DemandType(Enum):
    FILE_QUERY = auto()
    QA = auto()

# 查询结果数据模型
@dataclass
class QueryResult:
    """Search result after enrichment."""
    doc_id: str
    title: str
    relevance: float  # in percent
    summary: str
    #key_fields_summary: str
    high_freq_terms: Dict[str, int]

# LLM配置数据模型
@dataclass
class LLMConfig:
    """LLM-related runtime config."""
    model: str = "deepseek-chat"
    max_tokens: int = 512
    api_key: Optional[str] = None
    temperature: float = 0.2
    base_url: str = "https://api.deepseek.com"