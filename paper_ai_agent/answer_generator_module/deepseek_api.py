import json
import os
from typing import Optional
from openai import OpenAI
from .data_models import LLMConfig

# 调整配置文件路径（现在位于src目录下）
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "api_config.json")

def load_llm_config() -> LLMConfig:
    """从src目录下的JSON文件加载LLM配置，兼容apikeys.txt"""
    # 初始化默认配置
    config = LLMConfig()
    
    # 1. 读取JSON配置（优先）
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            deepseek_config = json_data.get("deepseek", {})
            
            # 只更新非空配置项
            if deepseek_config.get("model"):
                config.model = deepseek_config["model"]
            if deepseek_config.get("max_tokens"):
                config.max_tokens = deepseek_config["max_tokens"]
            if deepseek_config.get("api_key"):
                config.api_key = deepseek_config["api_key"]
            if deepseek_config.get("temperature"):
                config.temperature = deepseek_config["temperature"]
            if deepseek_config.get("base_url"):
                config.base_url = deepseek_config["base_url"]
    
    # 2. 兼容旧的apikeys.txt（如果JSON中未配置API密钥）
    if not config.api_key:
        apikey_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "apikeys.txt")
        if os.path.exists(apikey_path):
            with open(apikey_path, "r", encoding="utf-8") as f:
                config.api_key = f.read().strip()
    
    return config

def build_deepseek_client(config: LLMConfig) -> Optional[OpenAI]:
    """构建DeepSeek OpenAI客户端"""
    if not config.api_key:
        print("警告：未配置DeepSeek API密钥，请在api_config.json中填写")
        return None
    return OpenAI(
        api_key=config.api_key,
        base_url=config.base_url
    )