# DeepSeek API 交互模块

## 功能概述

这是一个完整的 DeepSeek API 交互模块，支持长对话、对话历史记录、JSON响应保存等功能。

## ✨ 主要特性

- ✅ **长对话支持** - 自动维护对话上下文，支持多轮对话
- ✅ **对话历史** - 在内存中缓存用户和助手的所有对话
- ✅ **JSON保存** - 自动将API响应保存为UTF-8编码的JSON文件
- ✅ **配置管理** - 支持从配置文件加载API密钥和参数
- ✅ **命令系统** - 支持多种交互命令（quit、clear、history等）
- ✅ **Token统计** - 实时显示Token使用情况
- ✅ **错误处理** - 完善的异常捕获和错误提示

## 📁 文件结构

```
answer_generator/
├── __init__.py                  # 模块初始化
├── deepseek_api.py              # DeepSeek API核心类
├── main.py                      # 基础版主程序
├── main_advanced.py             # 高级版主程序
├── config.json                  # 配置文件
└── README.md                    # 使用说明

DeepSeek_Responses/              # API响应保存目录（自动创建）
├── response_2025-10-19_143025.json
├── conversation_2025-10-19_143045.json
└── ...
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置API密钥

编辑 `config.json` 文件，填入你的 DeepSeek API Key：

```json
{
  "api_key": "YOUR_DEEPSEEK_API_KEY_HERE",
  "base_url": "https://api.deepseek.com/v1",
  "model": "deepseek-chat",
  "temperature": 1.0,
  "max_tokens": null,
  "system_prompt": "你是一个有帮助的AI助手。请用中文回答问题，保持友好和专业。"
}
```

### 3. 运行程序

**基础版**（手动输入API密钥）：
```bash
cd Project/answer_generator
python main.py
```

**高级版**（从配置文件加载）：
```bash
cd Project/answer_generator
python main_advanced.py
```

## 💬 使用示例

### 启动对话

```
==================================================
🤖 DeepSeek AI 对话助手 (高级版)
==================================================
✓ 从配置文件加载 API Key

正在初始化 DeepSeek API...
✅ 初始化成功！
   模型: deepseek-chat
   温度: 1.0
   响应保存: D:\...\DeepSeek_Responses

开始对话吧~

==================================================

👤 你: 你好！请介绍一下自己
```

### 长对话示例

```
👤 你: 什么是机器学习？

🤖 助手: 机器学习是人工智能的一个分支...

📊 本轮Token: 256 (提示: 128, 完成: 128) | 累计: 256
==================================================

👤 你: 能举个例子吗？

🤖 助手: 当然！比如图像识别...
（AI会记住之前的对话内容）

📊 本轮Token: 312 (提示: 180, 完成: 132) | 累计: 568
==================================================
```

### 使用命令

```
👤 你: history          # 查看对话历史
📝 对话历史 (共 5 条消息)
--------------------------------------------------
[1] 🔧 系统:
    你是一个有帮助的AI助手...

[2] 👤 用户:
    什么是机器学习？

[3] 🤖 助手:
    机器学习是人工智能的一个分支...
...

👤 你: stats            # 查看统计信息
📊 统计信息
--------------------------------------------------
对话轮次: 2
消息总数: 5
累计Token: 568
响应保存目录: D:\...\DeepSeek_Responses
--------------------------------------------------

👤 你: save             # 手动保存对话
✓ 对话历史已保存: D:\...\conversation_2025-10-19_143045.json

👤 你: clear            # 清空对话历史
✅ 对话历史已清空

👤 你: quit             # 退出程序
正在退出...
正在保存对话历史...
✓ 对话历史已保存: D:\...\conversation_2025-10-19_143100.json
👋 再见！
```

## 📚 API 使用

### DeepSeekAPI 类

```python
from answer_generator import DeepSeekAPI

# 初始化
api = DeepSeekAPI(api_key="your-api-key")

# 设置系统提示词
api.set_system_prompt("你是一个专业的编程助手")

# 发送消息
response = api.chat("如何学习Python？")

# 获取助手回复
assistant_message = api.get_last_assistant_message()

# 查看对话历史
history = api.get_history()

# 保存对话历史
api.save_conversation_history()

# 清空对话历史
api.clear_history()
```

### 完整示例

```python
from answer_generator import DeepSeekAPI

# 初始化API
api = DeepSeekAPI(api_key="your-api-key")

# 设置系统提示词
api.set_system_prompt("你是一个友好的AI助手")

# 进行多轮对话
questions = [
    "你好！",
    "什么是Python？",
    "它有什么优点？"
]

for question in questions:
    print(f"用户: {question}")
    response = api.chat(question)
    answer = api.get_last_assistant_message()
    print(f"助手: {answer}\n")

# 保存对话历史
api.save_conversation_history("my_conversation.json")
```

## ⚙️ 配置说明

### config.json 参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `api_key` | string | DeepSeek API密钥 | 必填 |
| `base_url` | string | API基础URL | `https://api.deepseek.com/v1` |
| `model` | string | 模型名称 | `deepseek-chat` |
| `temperature` | float | 温度参数(0-2) | `1.0` |
| `max_tokens` | int/null | 最大生成token数 | `null` |
| `system_prompt` | string | 系统提示词 | 默认助手提示词 |

### 温度参数说明

- **0.0-0.3**: 更确定、更保守的回答
- **0.7-1.0**: 平衡创造性和准确性（推荐）
- **1.3-2.0**: 更有创造性、更随机的回答

## 📂 JSON 文件格式

### API响应文件 (response_*.json)

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1697000000,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "这是AI的回复内容..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 128,
    "completion_tokens": 256,
    "total_tokens": 384
  }
}
```

### 对话历史文件 (conversation_*.json)

```json
{
  "timestamp": "2025-10-19T14:30:45.123456",
  "message_count": 5,
  "messages": [
    {
      "role": "system",
      "content": "你是一个有帮助的AI助手..."
    },
    {
      "role": "user",
      "content": "用户的问题"
    },
    {
      "role": "assistant",
      "content": "AI的回答"
    }
  ]
}
```

## 🎯 支持的命令

| 命令 | 说明 |
|------|------|
| `quit` / `exit` / `q` | 退出程序（自动保存对话） |
| `clear` | 清空对话历史 |
| `history` | 查看所有对话历史 |
| `save` | 手动保存对话历史 |
| `stats` | 查看统计信息（仅高级版） |

## 🔧 核心功能

### 1. 长对话支持

系统会自动将所有对话消息保存在内存中的 `conversation_history` 列表中，每次调用API时都会发送完整的对话历史，从而实现上下文感知的多轮对话。

```python
# 对话历史结构
conversation_history = [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户消息1"},
    {"role": "assistant", "content": "助手回复1"},
    {"role": "user", "content": "用户消息2"},
    {"role": "assistant", "content": "助手回复2"},
    ...
]
```

### 2. JSON响应保存

每次API调用后，原始响应会自动保存为JSON文件：

- 文件名格式：`response_YYYY-MM-DD_HHMMSS.json`
- 编码：UTF-8（完美支持中文）
- 位置：项目根目录下的 `DeepSeek_Responses` 文件夹

### 3. 退出时自动保存

当用户输入 `quit`、`exit` 或 `q` 退出程序时，系统会自动保存完整的对话历史到JSON文件。

## ⚠️ 注意事项

1. **API密钥安全**：不要将包含真实API密钥的 `config.json` 提交到Git仓库
2. **Token限制**：注意DeepSeek API的token限制，长对话可能超出限制
3. **费用控制**：API调用会产生费用，请合理使用
4. **网络连接**：需要稳定的网络连接访问DeepSeek API
5. **编码问题**：所有文件使用UTF-8编码，确保中文正常显示

## 🐛 故障排除

### 问题1: 无法连接API

```
❌ 请求失败: HTTPSConnectionPool...
```

**解决方案**：
- 检查网络连接
- 确认 `base_url` 配置正确
- 检查防火墙设置

### 问题2: API密钥无效

```
❌ 请求失败: 401 Unauthorized
```

**解决方案**：
- 检查API密钥是否正确
- 确认API密钥是否已激活
- 检查账户余额

### 问题3: 中文显示乱码

**解决方案**：
- 确保终端支持UTF-8编码
- Windows用户：`chcp 65001`
- 检查文件保存时使用UTF-8编码

### 问题4: Token超出限制

```
❌ 请求失败: 400 Bad Request (Token limit exceeded)
```

**解决方案**：
- 使用 `clear` 命令清空对话历史
- 减少单次输入的内容长度
- 设置 `max_tokens` 参数限制输出长度

## 📊 性能建议

1. **合理使用对话历史**：定期清空不需要的历史记录
2. **设置token限制**：避免生成过长的回复
3. **批量处理**：需要处理多个独立问题时，考虑清空历史
4. **监控费用**：定期检查API使用情况和费用

## 🔄 版本历史

- **v1.0.0** (2025-10-19)
  - ✅ 实现DeepSeek API交互
  - ✅ 支持长对话功能
  - ✅ JSON响应自动保存（UTF-8）
  - ✅ 配置文件管理
  - ✅ 完整的命令系统
  - ✅ 退出时自动保存

## 📞 技术支持

如遇到问题，请检查：
1. API密钥是否正确
2. 网络连接是否正常
3. 配置文件格式是否正确
4. 查看保存的JSON文件确认响应内容

---

**开发者**: STAT7008A Project Team  
**最后更新**: 2025-10-19  
**状态**: ✅ 功能完整，运行稳定
