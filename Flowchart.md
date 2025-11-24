# 项目总体流程图 (Chinese Version)

```mermaid
flowchart TD
    %% 主体结构: 入口 -> 配置 -> 蓝图 -> 模块 -> 数据 & 日志

    subgraph Client[客户端]
        User[用户请求 (浏览器 / 终端 / 调度)]
    end

    subgraph Launcher[启动器]
        AppStart[运行 __main__.py]
        RegisterBlueprints[注册蓝图]
    end

    subgraph Config[全局配置]
        LoadConfig[加载 app_settings.json]
    end

    subgraph API蓝图[Flask 蓝图]
        MainBP[主页路由]
        CrawlerBP[爬虫接口]
        ClassifierBP[文件分类]
        GeneratorBP[生成接口]
        DatabaseBP[数据库 CRUD]
        DownloadBP[文件下载]
        ExampleBP[示例测试]
    end

    subgraph 爬虫[crawler]
        WebCrawler[WebCrawler<br/>robots.txt<br/>随机代理]<br/>
        SaveFiles[保存原始文件]
    end

    subgraph 文件处理[file processing]
        PDFAnalysis[文本提取]
        PDFSplitEmbed[分块+Embedding]<br/>
        BM25[BM25 词频]
        SaveDB[写入结果]
    end

    subgraph 答案生成[answer gen]
        RAGPipeline[RAG 检索生成]
    end

    subgraph 数据库[database]
        Models[ORM 模型]
        Ops[查询更新]
    end

    subgraph 日志[logging]
        Logger[统一日志]
    end

    subgraph 资源与数据[持久化]
        Unclassified[原始文件]
        DBCommon[分析 JSON]
        DBEmbedding[向量 index]
        BM25Store[BM25 词频]
    end

    User --> AppStart --> LoadConfig --> RegisterBlueprints
    RegisterBlueprints --> MainBP
    User --> MainBP
    CrawlerBP --> WebCrawler --> SaveFiles --> PDFAnalysis
    PDFAnalysis --> PDFSplitEmbed --> SaveDB
    PDFSplitEmbed --> BM25Store
    ClassifierBP --> PDFAnalysis
    GeneratorBP --> RAGPipeline
    PDFSplitEmbed --> RAGPipeline
    RAGPipeline --> DBEmbedding
    RAGPipeline --> DBCommon
    DatabaseBP --> Ops --> Models
    WebCrawler --> Logger
    PDFAnalysis --> Logger
    PDFSplitEmbed --> Logger
    RAGPipeline --> Logger
    Ops --> Logger
    SaveFiles --> Unclassified
    SaveDB --> DBCommon
    SaveDB --> DBEmbedding
    PDFSplitEmbed --> BM25Store

    classDef entry fill:#ffe5cc,stroke:#ff9900,stroke-width:2;
    classDef api fill:#fffbe6,stroke:#d4b106,stroke-width:1;
    classDef process fill:#f9e6ff,stroke:#cc66ff,stroke-width:1;
    classDef storage fill:#f0ffe6,stroke:#66bb00,stroke-width:1;
    classDef service fill:#e6f7ff,stroke:#3399ff,stroke-width:1;

    AppStart,RegisterBlueprints,LoadConfig:::entry
    MainBP,CrawlerBP,ClassifierBP,GeneratorBP,DatabaseBP,DownloadBP,ExampleBP:::api
    WebCrawler,PDFAnalysis,PDFSplitEmbed,BM25,SaveDB,RAGPipeline,Ops:::process
    Unclassified,DBCommon,DBEmbedding,BM25Store:::storage
    Logger:::service
```

## 说明 (中文)

- 启动：`__main__.py` 初始化 Flask 并加载配置。
- 蓝图：路由分发至爬虫 / 文件处理 / 生成 / 数据库。
- 爬虫：支持 robots.txt 及随机代理，文件入 `Resource/Unclassified`。
- 文件处理：提取 -> 分块 + Embedding -> 索引构建 -> 结果入库。
- 生成：RAG 结合向量与结构化内容回答。
- 数据库：统一 CRUD 与检索操作。
- 日志：模块关键动作集中写入按日期目录。
- 数据：原始、分析、向量、词频分离存储便于增量维护。

---

## Project Flowchart (English Version)

```mermaid
flowchart TD
    %% Core path: Entry -> Config -> Blueprints -> Modules -> Data & Logs

    subgraph Client[Client]
        User[Request Source (Browser / CLI / Scheduler)]
    end

    subgraph Launcher[Launcher]
        AppStart[Run __main__.py]
        RegisterBlueprints[Register Blueprints]
    end

    subgraph Config[Global Config]
        LoadConfig[Load app_settings.json]
    end

    subgraph API[Flask Blueprints]
        MainBP[Main Routes]
        CrawlerBP[Crawler API]
        ClassifierBP[Classifier API]
        GeneratorBP[Generation API]
        DatabaseBP[Database CRUD]
        DownloadBP[Download API]
        ExampleBP[Examples]
    end

    subgraph Crawler[Crawler Module]
        WebCrawler[WebCrawler<br/>robots.txt<br/>Random Proxy]
        SaveFiles[Store Raw Files]
    end

    subgraph Processing[File Processing]
        PDFAnalysis[PDF Text Extract]
        PDFSplitEmbed[Chunk + Embed]
        BM25[BM25 Term Freq]
        SaveDB[Persist Results]
    end

    subgraph Generation[Answer Generation]
        RAGPipeline[RAG Pipeline]
    end

    subgraph Database[Database Layer]
        Models[ORM Models]
        Ops[Query / Update]
    end

    subgraph Logging[Logging]
        Logger[Unified Logger]
    end

    subgraph Storage[Persistent Data]
        Unclassified[Raw Files]
        DBCommon[Analysis JSON]
        DBEmbedding[Vector Index]
        BM25Store[BM25 term_freq]
    end

    User --> AppStart --> LoadConfig --> RegisterBlueprints
    RegisterBlueprints --> MainBP
    User --> MainBP
    CrawlerBP --> WebCrawler --> SaveFiles --> PDFAnalysis
    PDFAnalysis --> PDFSplitEmbed --> SaveDB
    PDFSplitEmbed --> BM25Store
    ClassifierBP --> PDFAnalysis
    GeneratorBP --> RAGPipeline
    PDFSplitEmbed --> RAGPipeline
    RAGPipeline --> DBEmbedding
    RAGPipeline --> DBCommon
    DatabaseBP --> Ops --> Models
    WebCrawler --> Logger
    PDFAnalysis --> Logger
    PDFSplitEmbed --> Logger
    RAGPipeline --> Logger
    Ops --> Logger
    SaveFiles --> Unclassified
    SaveDB --> DBCommon
    SaveDB --> DBEmbedding
    PDFSplitEmbed --> BM25Store

    classDef entry fill:#ffe5cc,stroke:#ff9900,stroke-width:2;
    classDef api fill:#fffbe6,stroke:#d4b106,stroke-width:1;
    classDef process fill:#f9e6ff,stroke:#cc66ff,stroke-width:1;
    classDef storage fill:#f0ffe6,stroke:#66bb00,stroke-width:1;
    classDef service fill:#e6f7ff,stroke:#3399ff,stroke-width:1;

    AppStart,RegisterBlueprints,LoadConfig:::entry
    MainBP,CrawlerBP,ClassifierBP,GeneratorBP,DatabaseBP,DownloadBP,ExampleBP:::api
    WebCrawler,PDFAnalysis,PDFSplitEmbed,BM25,SaveDB,RAGPipeline,Ops:::process
    Unclassified,DBCommon,DBEmbedding,BM25Store:::storage
    Logger:::service
```

## Explanation (English)

- Startup: Initialize Flask and load global configuration object.
- Routing: Blueprints dispatch requests to crawler, processing, generation, and database logic.
- Crawler: Respects robots.txt and rotates random proxies; stores raw files.
- Processing: Extract text, chunk + embed, build BM25 & vector index, persist structured outputs.
- Generation: RAG pipeline combines embeddings and stored analysis for answers.
- Database: Central CRUD for file records and metadata updates.
- Logging: All critical operations written to date-organized log directories.
- Storage: Separation of raw, analysis JSON, FAISS index, BM25 frequencies simplifies incremental updates.

---

```bash
mmdc -i Flowchart.md -o flowchart.png
```
