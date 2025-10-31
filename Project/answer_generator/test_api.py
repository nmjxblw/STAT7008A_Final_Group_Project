"""
DeepSeek API 功能测试
"""

import sys
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from answer_generator.deepseek_api import DeepSeekAPI


def test_api_initialization():
    """测试API初始化"""
    print("=" * 60)
    print("测试1: API初始化")
    print("=" * 60)

    try:
        api = DeepSeekAPI(api_key="test-key-12345")
        print(f"✓ API初始化成功")
        print(f"  - 对话历史长度: {len(api.get_history())}")
        print(f"  - 响应保存目录: {api.response_save_dir}")
        print(f"  - 目录存在: {api.response_save_dir.exists()}")
        return True
    except Exception as e:
        print(f"✗ API初始化失败: {e}")
        return False


def test_conversation_history():
    """测试对话历史管理"""
    print("\n" + "=" * 60)
    print("测试2: 对话历史管理")
    print("=" * 60)

    try:
        api = DeepSeekAPI(api_key="test-key")

        # 添加消息
        api.add_message("user", "你好")
        api.add_message("assistant", "你好！有什么我可以帮助你的吗？")
        api.add_message("user", "介绍一下自己")

        history = api.get_history()
        print(f"✓ 对话历史管理正常")
        print(f"  - 历史消息数: {len(history)}")
        print(f"  - 最后一条消息角色: {history[-1]['role']}")

        # 测试清空
        api.clear_history()
        print(f"  - 清空后消息数: {len(api.get_history())}")

        return True
    except Exception as e:
        print(f"✗ 对话历史管理失败: {e}")
        return False


def test_system_prompt():
    """测试系统提示词设置"""
    print("\n" + "=" * 60)
    print("测试3: 系统提示词设置")
    print("=" * 60)

    try:
        api = DeepSeekAPI(api_key="test-key")

        # 设置系统提示词
        api.set_system_prompt("你是一个专业的编程助手")

        history = api.get_history()
        print(f"✓ 系统提示词设置成功")
        print(f"  - 历史消息数: {len(history)}")
        print(f"  - 第一条消息角色: {history[0]['role']}")
        print(f"  - 提示词内容: {history[0]['content'][:50]}...")

        return True
    except Exception as e:
        print(f"✗ 系统提示词设置失败: {e}")
        return False


def test_save_load_history():
    """测试保存和加载对话历史"""
    print("\n" + "=" * 60)
    print("测试4: 保存和加载对话历史")
    print("=" * 60)

    try:
        api = DeepSeekAPI(api_key="test-key")

        # 添加一些对话
        api.add_message("user", "测试消息1")
        api.add_message("assistant", "测试回复1")
        api.add_message("user", "测试消息2")

        # 保存
        test_filename = "test_conversation.json"
        api.save_conversation_history(test_filename)

        # 清空
        api.clear_history()
        print(f"  - 清空后消息数: {len(api.get_history())}")

        # 加载
        filepath = api.response_save_dir / test_filename
        api.load_conversation_history(str(filepath))
        print(f"  - 加载后消息数: {len(api.get_history())}")

        print(f"✓ 保存和加载功能正常")

        # 清理测试文件
        if filepath.exists():
            filepath.unlink()
            print(f"  - 测试文件已清理")

        return True
    except Exception as e:
        print(f"✗ 保存和加载功能失败: {e}")
        return False


def test_get_last_message():
    """测试获取最后一条助手消息"""
    print("\n" + "=" * 60)
    print("测试5: 获取最后一条助手消息")
    print("=" * 60)

    try:
        api = DeepSeekAPI(api_key="test-key")

        # 添加对话
        api.add_message("user", "你好")
        api.add_message("assistant", "你好！有什么我可以帮助你的吗？")
        api.add_message("user", "谢谢")
        api.add_message("assistant", "不客气！")

        last_message = api.get_last_assistant_message()
        print(f"✓ 获取最后一条助手消息成功")
        print(f"  - 消息内容: {last_message}")

        return True
    except Exception as e:
        print(f"✗ 获取最后一条助手消息失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n🚀 开始测试 DeepSeek API 模块\n")

    results = []
    results.append(("API初始化", test_api_initialization()))
    results.append(("对话历史管理", test_conversation_history()))
    results.append(("系统提示词设置", test_system_prompt()))
    results.append(("保存和加载历史", test_save_load_history()))
    results.append(("获取最后消息", test_get_last_message()))

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过!")
        print("\n提示: 这些是基础功能测试，不包含实际API调用")
        print("要测试实际API调用，请使用 main.py 或 main_advanced.py")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
