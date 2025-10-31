"""
DeepSeek API 交互主程序
实现长对话功能，支持对话历史记录
"""

import sys
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from answer_generator import DeepSeekAPI


def print_separator(char: str = "=", length: int = 60):
    """打印分隔线"""
    print(char * length)


def print_welcome():
    """打印欢迎信息"""
    print_separator()
    print("🤖 DeepSeek AI 对话助手")
    print_separator()
    print("使用说明:")
    print("  - 直接输入消息与AI对话")
    print("  - 输入 'quit' 或 'exit' 退出程序")
    print("  - 输入 'clear' 清空对话历史")
    print("  - 输入 'history' 查看对话历史")
    print("  - 输入 'save' 保存当前对话")
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

        if role == "system":
            print(f"\n[{i}] 🔧 系统: {content[:100]}...")
        elif role == "user":
            print(f"\n[{i}] 👤 用户: {content}")
        elif role == "assistant":
            print(f"\n[{i}] 🤖 助手: {content}")

    print_separator("-")


def main():
    """主函数"""
    # 打印欢迎信息
    print_welcome()

    # 获取API密钥
    api_key = input("请输入你的 DeepSeek API Key: ").strip()

    if not api_key:
        print("❌ API Key 不能为空")
        return

    # 初始化API
    print("\n正在初始化 DeepSeek API...")
    api = DeepSeekAPI(api_key=api_key)

    # 设置系统提示词（可选）
    system_prompt = """你是一个有帮助的AI助手。请用中文回答问题，保持友好和专业。"""
    api.set_system_prompt(system_prompt)

    print("✅ 初始化成功！开始对话吧~\n")
    print_separator()

    # 对话循环
    message_count = 0

    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()

            # 检查退出命令
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n正在退出...")

                # 询问是否保存对话历史
                if message_count > 0:
                    save_choice = input("是否保存对话历史? (y/n): ").strip().lower()
                    if save_choice == "y":
                        api.save_conversation_history()

                print("👋 再见！")
                break

            # 检查清空历史命令
            if user_input.lower() == "clear":
                api.clear_history()
                # 重新设置系统提示词
                api.set_system_prompt(system_prompt)
                print("✅ 对话历史已清空")
                message_count = 0
                continue

            # 检查查看历史命令
            if user_input.lower() == "history":
                display_history(api)
                continue

            # 检查保存命令
            if user_input.lower() == "save":
                api.save_conversation_history()
                continue

            # 检查空输入
            if not user_input:
                print("⚠️  请输入内容")
                continue

            # 发送消息到API
            print("\n🤖 助手: ", end="", flush=True)

            try:
                response = api.chat(user_input)

                # 提取并显示助手回复
                if "choices" in response and len(response["choices"]) > 0:
                    assistant_message = response["choices"][0]["message"]["content"]
                    print(assistant_message)
                    message_count += 1

                    # 显示token使用情况
                    if "usage" in response:
                        usage = response["usage"]
                        print(
                            f"\n📊 Token使用: {usage.get('total_tokens', 'N/A')} "
                            f"(提示: {usage.get('prompt_tokens', 'N/A')}, "
                            f"完成: {usage.get('completion_tokens', 'N/A')})"
                        )
                else:
                    print("❌ 未收到有效回复")

            except Exception as e:
                print(f"❌ 请求失败: {e}")
                print("提示: 请检查API密钥是否正确，或网络连接是否正常")

            print_separator()

        except KeyboardInterrupt:
            print("\n\n检测到 Ctrl+C，正在退出...")
            if message_count > 0:
                save_choice = input("是否保存对话历史? (y/n): ").strip().lower()
                if save_choice == "y":
                    api.save_conversation_history()
            print("👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            continue


if __name__ == "__main__":
    main()
