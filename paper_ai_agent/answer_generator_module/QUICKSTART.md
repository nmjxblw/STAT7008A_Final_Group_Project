# DeepSeek API 快速开始指南

## ✅ 已实现的功能

根据你的要求，我已经完成以下功能：

### 1. ✅ DeepSeek API交互功能（在main.py中）
- 完整的API调用封装
- 支持自定义模型参数（temperature, max_tokens等）
- 错误处理和异常捕获

### 2. ✅ JSON响应保存（UTF-8格式）
- 所有API响应自动保存到根目录 `DeepSeek_Responses/`
- 文件名格式：`response_2025-10-19_143025.json`
- 使用 UTF-8 编码，完美支持中文

### 3. ✅ 长对话功能（对话缓存）
- 在内存中维护完整的对话历史
- 每次API调用自动包含历史上下文
- 支持多轮对话，AI能记住之前的内容

### 4. ✅ 输入"quit"退出循环
- 支持 `quit`, `exit`, `q` 三种退出命令
- 退出前自动保存对话历史
- 支持 Ctrl+C 快捷退出

## 🚀 快速使用

### 方式1: 基础版（手动输入API密钥）

```bash
cd Project/answer_generator
python main.py
```

启动后：
1. 输入你的 DeepSeek API Key
2. 开始对话
3. 输入 `quit` 退出

### 方式2: 高级版（配置文件管理）

1. 编辑 `config.json`，填入API密钥：
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxx"
}
```

2. 运行程序：
```bash
cd Project/answer_generator
python main_advanced.py
```

## 📋 功能演示

### 长对话示例

```
👤 你: Python是什么？

🤖 助手: Python是一种高级编程语言...

👤 你: 它有什么优点？
      ↑ AI会记住之前讨论的是Python

🤖 助手: Python的主要优点包括...
```

### JSON保存示例

每次对话都会在 `DeepSeek_Responses/` 生成JSON文件：

**response_2025-10-19_143025.json**:
```json
{
  "id": "chatcmpl-xxx",
  "model": "deepseek-chat",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "AI的回复内容..."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 128,
    "completion_tokens": 256,
    "total_tokens": 384
  }
}
```

### 对话历史保存

退出时自动生成 `conversation_YYYY-MM-DD_HHMMSS.json`:

```json
{
  "timestamp": "2025-10-19T14:30:45.123456",
  "message_count": 6,
  "messages": [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户问题1"},
    {"role": "assistant", "content": "AI回答1"},
    {"role": "user", "content": "用户问题2"},
    {"role": "assistant", "content": "AI回答2"}
  ]
}
```

## 🎯 核心代码示例

### 使用DeepSeekAPI类

```python
from answer_generator.deepseek_api import DeepSeekAPI

# 初始化
api = DeepSeekAPI(api_key="your-api-key")

# 设置系统提示词
api.set_system_prompt("你是一个专业的助手")

# 进行对话
response1 = api.chat("Python是什么？")
print(api.get_last_assistant_message())

# 继续对话（AI会记住上下文）
response2 = api.chat("它有什么优点？")
print(api.get_last_assistant_message())

# 查看完整历史
history = api.get_history()
print(f"共 {len(history)} 条消息")

# 保存对话
api.save_conversation_history()
```

## 📁 文件结构

```
Project/
└── answer_generator/
    ├── __init__.py              # 模块初始化
    ├── deepseek_api.py          # ✅ API核心类
    ├── main.py                  # ✅ 基础版主程序
    ├── main_advanced.py         # ✅ 高级版主程序
    ├── config.json              # ✅ 配置文件
    ├── test_api.py              # ✅ 测试脚本
    └── README.md                # ✅ 详细文档

DeepSeek_Responses/              # ✅ 响应保存目录（自动创建）
├── response_2025-10-19_143025.json
├── response_2025-10-19_143030.json
├── conversation_2025-10-19_143100.json
└── ...
```

## 🧪 运行测试

测试基础功能：
```bash
cd Project/answer_generator
python test_api.py
```

测试结果：
```
🎉 所有测试通过!
总计: 5/5 测试通过

✓ API初始化
✓ 对话历史管理
✓ 系统提示词设置
✓ 保存和加载历史
✓ 获取最后消息
```

## 💡 使用技巧

### 1. 清空历史以开始新话题

```
👤 你: clear
✅ 对话历史已清空
```

### 2. 查看对话历史

```
👤 你: history
📝 对话历史 (共 5 条消息)
[1] 🔧 系统: 你是一个有帮助的AI助手...
[2] 👤 用户: 问题1
[3] 🤖 助手: 回答1
...
```

### 3. 手动保存对话

```
👤 你: save
✓ 对话历史已保存
```

### 4. 查看统计信息（高级版）

```
👤 你: stats
📊 统计信息
--------------------------------------------------
对话轮次: 3
消息总数: 7
累计Token: 1024
```

## ⚙️ 自定义配置

编辑 `config.json` 来自定义行为：

```json
{
  "api_key": "your-key",
  "model": "deepseek-chat",
  "temperature": 0.7,          // 较低=更确定，较高=更有创造性
  "max_tokens": 2000,          // 限制输出长度
  "system_prompt": "你是..."   // 自定义AI角色
}
```

## 🔑 获取API密钥

1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账号
3. 进入API管理页面
4. 创建新的API密钥
5. 复制密钥到 `config.json` 或启动时输入

## ❓ 常见问题

### Q: 如何实现长对话？
A: 系统自动维护对话历史，每次调用API都会发送完整历史。

### Q: JSON文件保存在哪里？
A: 项目根目录的 `DeepSeek_Responses/` 文件夹（自动创建）。

### Q: 如何退出程序？
A: 输入 `quit`、`exit` 或 `q`，或按 `Ctrl+C`。

### Q: 对话历史会自动保存吗？
A: 是的，退出时自动保存。也可以输入 `save` 手动保存。

### Q: 支持中文吗？
A: 完全支持！所有文件使用UTF-8编码。

## 📊 性能说明

- **响应时间**: 取决于DeepSeek API服务器
- **内存使用**: 对话历史存储在内存中
- **文件大小**: JSON文件通常几KB到几十KB
- **并发支持**: 单线程顺序处理

## 🎉 完成状态

- ✅ **需求1**: DeepSeek API交互功能 - 已完成
- ✅ **需求2**: JSON响应UTF-8保存 - 已完成  
- ✅ **需求3**: 长对话功能和缓存 - 已完成
- ✅ **需求4**: quit命令退出循环 - 已完成

**所有功能均已实现并通过测试！** 🚀

---

**开发完成时间**: 2025-10-19  
**测试状态**: ✅ 5/5 通过  
**功能状态**: ✅ 完全可用
