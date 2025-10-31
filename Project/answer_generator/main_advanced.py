"""
DeepSeek API 交互主程序 (高级版)
支持从配置文件加载API密钥，实现长对话功能
"""

import sys
import json
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from answer_generator import DeepSeekAPI


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(__file__).parent / config_path
        self.config = self.load_config()

    def load_config(self) -> dict:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  配置文件未找到: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return {}

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置已保存: {self.config_path}")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")


def print_separator(char: str = "=", length: int = 60):
    """打印分隔线"""
    print(char * length)


def print_welcome():
    """打印欢迎信息"""
    print_separator()
    print("🤖 DeepSeek AI 对话助手 (高级版)")
    print_separator()
    print("功能特性:")
    print("  ✓ 长对话支持 - 自动维护对话上下文")
    print("  ✓ 历史记录 - 自动保存所有API响应")
    print("  ✓ UTF-8编码 - 完美支持中文")
    print()
    print("命令列表:")
    print("  'quit' / 'exit' / 'q' - 退出程序")
    print("  'clear' - 清空对话历史")
    print("  'history' - 查看对话历史")
    print("  'save' - 手动保存对话")
    print("  'stats' - 查看统计信息")
    print_separator()
    print()


def display_history(api: DeepSeekAPI):
    """显示对话历史"""
    history = api.get_history()
    if not history:
        print("📝 对话历史为空")
        return

    print_separator("-")
    print(f"📝 对话历史 (共 {len(history)} 条消息)")
    print_separator("-")

    for i, message in enumerate(history, 1):
        role = message["role"]
        content = message["content"]

        # 限制显示长度
        max_length = 200
        display_content = (
            content if len(content) <= max_length else content[:max_length] + "..."
        )

        if role == "system":
            print(f"\n[{i}] 🔧 系统:")
            print(f"    {display_content}")
        elif role == "user":
            print(f"\n[{i}] 👤 用户:")
            print(f"    {display_content}")
        elif role == "assistant":
            print(f"\n[{i}] 🤖 助手:")
            print(f"    {display_content}")

    print_separator("-")


def display_stats(api: DeepSeekAPI, message_count: int, total_tokens: int):
    """显示统计信息"""
    print_separator("-")
    print("📊 统计信息")
    print_separator("-")
    print(f"对话轮次: {message_count}")
    print(f"消息总数: {len(api.get_history())}")
    print(f"累计Token: {total_tokens}")
    print(f"响应保存目录: {api.response_save_dir}")
    print_separator("-")


def main():
    """主函数"""
    # 打印欢迎信息
    print_welcome()

    # 加载配置
    config = Config()

    # 获取API密钥
    api_key = config.get("api_key", "")

    # 如果配置文件中没有API密钥，则提示输入
    if not api_key or api_key == "YOUR_DEEPSEEK_API_KEY_HERE":
        api_key = input("请输入你的 DeepSeek API Key: ").strip()

        if not api_key:
            print("❌ API Key 不能为空")
            return

        # 询问是否保存到配置文件
        save_choice = input("是否保存API Key到配置文件? (y/n): ").strip().lower()
        if save_choice == "y":
            config.config["api_key"] = api_key
            config.save_config()
    else:
        print(f"✓ 从配置文件加载 API Key")

    # 初始化API
    print("\n正在初始化 DeepSeek API...")
    base_url = config.get("base_url", "https://api.deepseek.com/v1")
    api = DeepSeekAPI(api_key=api_key, base_url=base_url)

    # 设置系统提示词
    system_prompt = config.get(
        "system_prompt", "你是一个有帮助的AI助手。请用中文回答问题，保持友好和专业。"
    )
    api.set_system_prompt(system_prompt)

    # 获取模型参数
    model = config.get("model", "deepseek-chat")
    temperature = config.get("temperature", 1.0)
    max_tokens = config.get("max_tokens", None)

    print(f"✅ 初始化成功！")
    print(f"   模型: {model}")
    print(f"   温度: {temperature}")
    print(f"   响应保存: {api.response_save_dir}")
    print("\n开始对话吧~\n")
    print_separator()

    # 对话循环
    message_count = 0
    total_tokens = 0

    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()

            # 检查退出命令
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n正在退出...")

                # 自动保存对话历史
                if message_count > 0:
                    print("正在保存对话历史...")
                    api.save_conversation_history()
                    display_stats(api, message_count, total_tokens)

                print("👋 再见！")
                break

            # 检查清空历史命令
            if user_input.lower() == "clear":
                api.clear_history()
                # 重新设置系统提示词
                api.set_system_prompt(system_prompt)
                print("✅ 对话历史已清空")
                message_count = 0
                total_tokens = 0
                continue

            # 检查查看历史命令
            if user_input.lower() == "history":
                display_history(api)
                continue

            # 检查保存命令
            if user_input.lower() == "save":
                api.save_conversation_history()
                continue

            # 检查统计信息命令
            if user_input.lower() == "stats":
                display_stats(api, message_count, total_tokens)
                continue

            # 检查空输入
            if not user_input:
                print("⚠️  请输入内容")
                continue

            # 发送消息到API
            print("\n🤖 助手: ", end="", flush=True)

            try:
                response = api.chat(
                    user_input,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # 提取并显示助手回复
                if "choices" in response and len(response["choices"]) > 0:
                    assistant_message = response["choices"][0]["message"]["content"]
                    print(assistant_message)
                    message_count += 1

                    # 显示token使用情况
                    if "usage" in response:
                        usage = response["usage"]
                        tokens_used = usage.get("total_tokens", 0)
                        total_tokens += tokens_used
                        print(
                            f"\n📊 本轮Token: {tokens_used} "
                            f"(提示: {usage.get('prompt_tokens', 0)}, "
                            f"完成: {usage.get('completion_tokens', 0)}) "
                            f"| 累计: {total_tokens}"
                        )
                else:
                    print("❌ 未收到有效回复")
                    print(f"原始响应: {response}")

            except Exception as e:
                print(f"❌ 请求失败: {e}")
                print("提示: 请检查API密钥是否正确，或网络连接是否正常")

            print_separator()

        except KeyboardInterrupt:
            print("\n\n检测到 Ctrl+C，正在退出...")
            if message_count > 0:
                print("正在保存对话历史...")
                api.save_conversation_history()
                display_stats(api, message_count, total_tokens)
            print("👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback

            traceback.print_exc()
            continue


if __name__ == "__main__":
    main()
