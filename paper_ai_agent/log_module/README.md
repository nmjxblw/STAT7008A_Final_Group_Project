# 高级日志系统使用指南

## ✨ 功能特性

根据你的需求，我已经实现了一个完整的高级日志系统：

### ✅ 已实现的功能

1. **按日期创建文件夹** - 格式: `yyyyMMdd`，示例: `./logs/20250910/`
2. **按时间命名日志文件** - 格式: `HHmmss_fff.log`，示例: `220512_089.log`
3. **UTF-8编码** - 完美支持中文和特殊字符
4. **自定义日志格式** - `[%(asctime)s][%(filename)s][%(levelname)s] - %(message)s`
   - ✨ **新特性**: 现在显示**调用脚本的文件名**，而不是logger名称
   - 可以快速定位日志来源文件
5. **完整路径示例** - `./logs/20250910/220512_089.log`

## 🚀 快速开始

```python
from log_mode.advanced_logger import setup_logger
import logging

# 创建日志记录器
logger = setup_logger("MyApp", level=logging.INFO)

# 开始记录日志
logger.info("应用程序启动")
logger.warning("警告信息")
logger.error("错误信息")
```

生成的日志文件: `./logs/20251102/143025_123.log`

**日志内容示例**:
```
[2025-11-02 14:30:25][my_script.py][INFO] - 应用程序启动
[2025-11-02 14:30:25][my_script.py][WARNING] - 警告信息
[2025-11-02 14:30:25][my_script.py][ERROR] - 错误信息
```

注意：日志中显示的是 `my_script.py`（调用日志的文件名），而不是 `MyApp`（logger名称）。

## 📊 测试结果

运行 `python log_mode/test_logger.py`:

```
🎉 所有测试通过!
总计: 7/7 测试通过
```

## 📖 详细文档

- **格式配置指南**: 查看 `FORMAT_GUIDE.md` 了解所有可用的日志格式选项
- **使用示例**: 查看 `example_usage.py` 了解各种使用场景
- **测试脚本**: 运行 `test_filename.py` 查看文件名显示效果

---

**状态**: ✅ 功能完整，可立即使用  
**测试**: ✅ 7/7 通过  
**最新更新**: 日志格式改为显示文件名（`%(filename)s`）
