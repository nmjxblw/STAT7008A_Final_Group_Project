# 需求表

## 网页爬虫 daily_crawling

- [ ] 1. 初次运行 daily_crawling.exe 软件时，将软件运行写入注册表，之后每次电脑启动时，自动运行本程序。（可选）
- [ ] 2. 程序启动后自动后台运行，在菜单栏中提供用户退出程序的选项。（可选）
- [ ] 3. 读取配置文件表 crawling_config.json（必须）：
  - [ ] 1. 每日爬虫的时间点 （e.g. `trigger_time:"8:00AM,UTC+08:00"`）（必须）
  - [ ] 2. 爬虫网站清单 （e.g. `crawling_source_list:["arxiv.org/catchup/cs.CV/2025-09-30?abs=True","https://scholar.google.com/?hl=zh-CN"...]`）（可选）
  - [ ] 3. 禁止访问的网站清单（可选）
  - [ ] 4. 爬虫关键词设置（e.g. `crawling_keywords:["[Pp]aper","[Ee]ssay"...]`）（可选）
  - [ ] 5. 爬虫文件类型设置（e.g. `file_type:[".pdf",".txt",".jpg",".png"...]`）（可选）
  - [ ] 6. 爬虫文件时效性设置，单位：天（e.g. `timeliness:365`）（可选）
- [ ] 4. 根据配置表内容执行爬虫任务（必须）
  - [ ] 1. 文件类型分析功能（必须）
    - [ ] 1.爬取.pdf 文件（必须）
    - [ ] 2.根据文件类型爬取（可选）
    - [ ] 3.根据关键词爬取（可选）
    - [ ] 4.根据文件时效性爬取（可选）
  - [ ] 2. 访问并爬取网站功能（必须）
    - [ ] 1.[arXiv website](https://arxiv.org/catchup/cs.CV/2025-09-30?abs=True)（必须）
    - [ ] 2. 根据爬取清单访问并爬取网页（可选）
    - [ ] 3. 全网爬取，但避开禁止爬取的网页（可选）
  - [ ] 3. 提供 API 接口，用于前端下发爬虫任务 （e.g. `def start_crawling_task()->bool`）（必须）
  - [ ] 4. 提供 API 接口，用于前端实时数据显示（可选）：
    - [ ] 1.当前正在爬取的网页 （e.g. `def get_current_crawling_web()->str`）（可选）
    - [ ] 2.当前正在爬取的文章 （e.g. `def get_current_crawling_article()->str`）（可选）
    - [ ] 3. 爬取的工作进度 （e.g. `def get_crawling_task_progress()->float`）（可选）
- [ ] 5. 将爬取到的文件存储至根目录下的 Resources 文件夹中的 Unclassified 文件夹中（e.g. `./Resource/Unclassified/MyPdf.pdf`）（必须）
  - [ ] 按照日期和格式分类（e.g. `"./Resource/Unclassified/PDF/2025-10-17_225143/Paper.pdf","./Resource/Unclassified/PNG/2025-10-18_001234/Screenshot.png"...`）（可选）
- [ ] 6. 在根目录 Crawling Log 中生成爬取清单日志（e.g. `./Crawling Log/2025-10-17_225143.log`）（可选）
  - [ ] 日志示例（e.g. `[2025-10-17 22:51:43] FileName:"Paper.pdf" Url:".../Paper.pdf"`）（可选）
- [ ] 7. 运行时异常捕获处理（可选）

## 文档归档智能体 file_classifier

- [ ] 1. 文档解析（必须）
  - [ ] 1. 使用第三方库实现.pdf 文件文本解析 （e.g. PyPDF2/pdfplumber/PyMuPDF）（必须）
    - [ ] 从`./Resource/Unclassified`目录下查找未归档的文档 -> 进行归档任务 -> 将归档后的文档存放于`./Resource/Classified`文件夹中对应的位置，并移除`./Resource/Unclassified`对应的文档。（必须）
  - [ ] 2. 使用第三方库扫描.pdf 文件中的图像信息，并转换成文本 （e.g. 第三方库：pytesseract/ pdf2image）（可选）
- [ ] 2. 文本预处理与特征提取（暂定）
  - [ ] 1. 使用第三方库，对文本进行清洗、词汇分离、去停用词；使用 TF-IDF 算法将文本向量化。将非结构化文本转为机器学习模型可读数值特征 （e.g. 第三方库：nltk/ sklearn）（暂定）
  - [ ] 2. 提取文档关键词和高频词 （top5，重点关注名词和实义动词），生成文档标签 tag (重点关注名词和文章标题)。（e.g. 高频词和关键词`term_frequency:dict[str:int] = {'attention':151,'need':70,'neural network':67,'algorithm':50,'ai':50}`，文档标签 tag `tags:list[str] = ["machine learning","attention mechanism","artificial intelligence"...]`）（必须）
  - [ ] 3. 提取文章描述概要。（暂定）
  - [ ] 4. 将提取出来的文章信息（特征值、高频关键词、标签、概要...）存储到本地数据集（.json/.csv/.xlsx...）中，以支持解答智能体查询相关文档。（必须）
    - [ ] 1.支持百万数量级并发读写，线程安全。（可选）
    - [ ] 2.采用数据库存储读写。（可选）
- [ ] 3. 提供 API 接口，用于前端下发文档处理任务。（e.g. `def start_file_classify_task()->bool`）（必须）
- [ ] 4. 提供 API 接口，用于前端下发导入分析结果任务，以excel格式导出。（e.g. `def export_analysis_to_excel()->bool`）（必须）

## 解答智能体 answer_generator

- [ ] 1. 提供 API 接口，用于处理前端输入用户的提问和需求。（e.g. `def set_demand(user_input:str)->`）
  - [ ] 1. 对用户需求进行分析并分类
    - [ ] 1. 

## Web 前端 index.html

- [ ] 1. 可交互前端
