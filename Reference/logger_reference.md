# 🎯 日志格式快速参考

## 当前配置

```python
log_format = "[%(asctime)s][%(filename)s][%(levelname)s] - %(message)s"
```

## 输出示例

```text
[2025-11-02 00:29:12][my_script.py][INFO] - 这是一条日志
```

## 核心变更

| 属性              | 显示内容               | 示例                 |
| ----------------- | ---------------------- | -------------------- |
| `%(filename)s` ✅ | **文件名**（当前使用） | `test.py`            |
| `%(name)s`        | Logger 名称            | `MyLogger`           |
| `%(pathname)s`    | 完整路径               | `D:/project/test.py` |
| `%(module)s`      | 模块名                 | `test`               |
| `%(funcName)s`    | 函数名                 | `main`               |
| `%(lineno)d`      | 行号                   | `42`                 |

## 快速使用

```python
from log_mode.logger import setup_logger

logger = setup_logger("MyApp")
logger.info("这是一条日志")
```

日志自动保存到: `./logs/20251102/002912_528.log`

## 更多信息

- 📖 完整格式列表: `FORMAT_GUIDE.md`
- 🧪 测试脚本: `test_filename.py`
- 📚 使用文档: `README.md`
