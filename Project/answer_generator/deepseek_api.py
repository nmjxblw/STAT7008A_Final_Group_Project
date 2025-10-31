"""
DeepSeek API 交互模块
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class DeepSeekAPI:
    """DeepSeek API 交互类"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        """
        初始化 DeepSeek API

        参数:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.conversation_history: List[Dict[str, str]] = []

        # 设置保存路径
        self.project_root = Path(__file__).parent.parent.parent
        self.response_save_dir = self.project_root / "DeepSeek_Responses"
        self.response_save_dir.mkdir(parents=True, exist_ok=True)

    def add_message(self, role: str, content: str):
        """
        添加消息到对话历史

        参数:
            role: 角色 ("user" 或 "assistant" 或 "system")
            content: 消息内容
        """
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history

    def chat(
        self,
        user_message: str,
        model: str = "deepseek-chat",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """
        发送聊天请求到 DeepSeek API

        参数:
            user_message: 用户消息
            model: 模型名称
            temperature: 温度参数 (0-2)
            max_tokens: 最大生成token数

        返回:
            API响应的JSON数据

        异常:
            requests.exceptions.RequestException: 网络请求异常
        """
        # 添加用户消息到历史
        self.add_message("user", user_message)

        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": self.conversation_history,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()

            # 解析响应
            response_data = response.json()

            # 提取助手回复
            if "choices" in response_data and len(response_data["choices"]) > 0:
                assistant_message = response_data["choices"][0]["message"]["content"]
                self.add_message("assistant", assistant_message)

            # 保存响应到文件
            self.save_response(response_data)

            return response_data

        except requests.exceptions.RequestException as e:
            error_data = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
            }
            self.save_response(error_data, is_error=True)
            raise

    def save_response(self, response_data: Dict, is_error: bool = False):
        """
        保存API响应到JSON文件

        参数:
            response_data: 响应数据
            is_error: 是否为错误响应
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        prefix = "error" if is_error else "response"
        filename = f"{prefix}_{timestamp}.json"
        filepath = self.response_save_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            print(f"✓ 响应已保存: {filepath}")
        except Exception as e:
            print(f"✗ 保存响应失败: {e}")

    def save_conversation_history(self, filename: Optional[str] = None):
        """
        保存对话历史到JSON文件

        参数:
            filename: 文件名 (可选)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"

        filepath = self.response_save_dir / filename

        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(self.conversation_history),
            "messages": self.conversation_history,
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            print(f"✓ 对话历史已保存: {filepath}")
        except Exception as e:
            print(f"✗ 保存对话历史失败: {e}")

    def load_conversation_history(self, filepath: str):
        """
        从JSON文件加载对话历史

        参数:
            filepath: 文件路径
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.conversation_history = data.get("messages", [])
            print(f"✓ 对话历史已加载: {filepath}")
        except Exception as e:
            print(f"✗ 加载对话历史失败: {e}")

    def get_last_assistant_message(self) -> Optional[str]:
        """获取最后一条助手消息"""
        for message in reversed(self.conversation_history):
            if message["role"] == "assistant":
                return message["content"]
        return None

    def set_system_prompt(self, system_prompt: str):
        """
        设置系统提示词

        参数:
            system_prompt: 系统提示词内容
        """
        # 移除旧的系统提示词
        self.conversation_history = [
            msg for msg in self.conversation_history if msg["role"] != "system"
        ]
        # 在开头添加新的系统提示词
        self.conversation_history.insert(
            0, {"role": "system", "content": system_prompt}
        )
