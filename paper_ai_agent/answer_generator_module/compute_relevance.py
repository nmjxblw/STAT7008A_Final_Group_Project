from typing import List, Set
import re
from .data_models import Document

class RelevanceCalculator:
    """独立的文档相关性计算工具类"""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """文本分词（仅保留字母数字，转为小写）"""
        return [t for t in re.split(r"[^0-9a-zA-Z]+", text.lower()) if t]
    
    @staticmethod
    def compute_relevance(query_tokens: List[str], doc: Document) -> float:
        """
        计算查询与文档的相关性得分（0-1之间）
        得分由三部分组成：关键词重叠得分（60%）、标签匹配加分（20%）、标题匹配加分（30%）
        """
        if not query_tokens:
            return 0.0

        # 合并文档所有文本字段（摘要+标题+关键词）
        doc_text = f"{doc.summary} {doc.title} {' '.join(doc.keywords)}"
        doc_tokens = RelevanceCalculator.tokenize(doc_text)

        # 转换为集合用于快速匹配
        query_set: Set[str] = set(query_tokens)
        doc_set: Set[str] = set(doc_tokens)

        # 1) 关键词重叠得分（占比60%）
        matched_keywords = len(query_set & doc_set)
        keyword_score = matched_keywords / len(query_set) if query_set else 0.0

        # 2) 标签匹配加分（最多加0.4分，占比20%）
        tag_matches = sum(1 for tag in doc.keywords if tag.lower() in query_set)
        tag_score = min(tag_matches, 2) * 0.2  # 限制最多匹配2个标签

        # 3) 标题匹配加分（每个匹配词加0.3分，占比30%）
        title_tokens = RelevanceCalculator.tokenize(doc.title)
        title_matched = len(query_set & set(title_tokens))
        title_score = title_matched * 0.3

        # 加权求和得到总得分
        total_score = (keyword_score * 0.6) + tag_score + title_score
        return min(total_score, 1.0)  # 限制得分不超过1.0

# 提供单例实例（方便全局使用）
relevance_calculator = RelevanceCalculator()