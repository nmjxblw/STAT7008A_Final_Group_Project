from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# 需求类型枚举
class DemandType(Enum):
    FILE_QUERY = auto()
    QA = auto()

# 文档数据模型
@dataclass
class Document:
    """Internal representation of a document in your KB."""
    file_id: str
    file_name: str
    title: str
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    text_length: int = 0
    file_type: str = "pdf"     # text / pdf / image / others
    extra_fields: Dict[str, Any] = field(default_factory=dict)

# 查询结果数据模型
@dataclass
class QueryResult:
    """Search result after enrichment."""
    doc_id: str
    title: str
    relevance: float  # in percent
    summary: str
    key_fields_summary: str
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