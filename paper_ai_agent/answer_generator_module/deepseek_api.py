import json
import os
from pathlib import Path
from typing import Optional
from openai import OpenAI
from .data_models import LLMConfig
from global_module import answer_generator_config, API_KEY

# 调整配置文件路径（现在位于src目录下）
CONFIG_PATH = Path(os.getcwd()) / "api_config.json"


def build_deepseek_client() -> Optional[OpenAI]:
    """构建DeepSeek OpenAI客户端"""
    if not API_KEY or API_KEY.strip() == "":
        print("警告：未配置DeepSeek API密钥，请在.env中填写")
        return None
    return OpenAI(api_key=API_KEY, base_url=answer_generator_config.base_url)
