# 爬虫模块 (Crawling Mode)

## 功能概述

这是一个功能完整的网页爬虫系统,支持定时爬取、文件分类存储、日志记录等功能。

## 主要功能

### 已实现的必需功能 ✅

- ✅ 读取配置文件 `crawling_config.json`
- ✅ 爬取 PDF 文件
- ✅ 根据文件类型爬取
- ✅ 根据关键词爬取
- ✅ 访问并爬取网站
- ✅ 提供 API 接口用于前端下发爬虫任务
- ✅ 提供 API 接口用于前端实时数据显示
- ✅ 将爬取的文件存储至 `./Resource/Unclassified` 目录
- ✅ 按照日期和格式分类存储
- ✅ 在根目录 `Crawling Log` 中生成爬取清单日志
- ✅ 运行时异常捕获处理

## 配置文件

配置文件位于: `Project/crawling_mode/crawling_config.json`

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
cd Project
python test_crawler.py
```

### 3. 启动主程序

```bash
cd Project
python main.py
```

## API接口

- POST /start - 启动爬虫任务
- GET /status/current_web - 获取当前爬取的网站
- GET /status/current_article - 获取当前爬取的文章
- GET /status/progress - 获取任务进度
