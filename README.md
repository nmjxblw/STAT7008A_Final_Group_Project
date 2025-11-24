# STAT7008A: Programming for Data Science (Fall 2025) - Final Group Project - Group 19

## Members

- Zhang Yinan
- PANG Boyang
- Li Xu
- Nie Chunjing
- WANG Qihao
- Chen Zhuo

## Initialized the Virtual Environment

[Virtual Environment List(.txt)](./requirements.txt)

```powershell
# run venv module
python -m venv .venv
# active venv
.venv/Scripts/activate
# install requirements form requirements.txt
pip install -r requirements.txt
# for MacOS user, you may need to run requirements_macos.txt instead.
# pip install -r requirements_macos.txt
```

## Setup the Config Files

- Enter the [program folder](./paper_ai_agent)
- Check and setup the [.env(.env)](./paper_ai_agent/.env) environment config file.
  - You may need to create one from [.env.example(.env.example)](./paper_ai_agent/.env.example) dotenv template file.
  - Setup your APIKEY of Deepseek in .env. Otherwise, you may not run this program.
- Check and setup the [app_settings(.json)](./paper_ai_agent/app_settings.json) application settings json file.
  - Generally, you do not need to modify it.
- Check and setup the [app_database(.db)](./paper_ai_agent/DB/app_database.db) sqlite database file.

## Run the Project

```powershell
# set the "paper_ai_agent" as the root
cd ./paper_ai_agent
# run the launcher script
python __main__.py
```

## Flowchart and Module Functions Description

```mermaid
flowchart TD
    %% Core path: Entry -> Config -> Blueprints -> Modules -> Data & Logs

    subgraph Service["Service"]
        User["Request Source: Browser / CLI / Scheduler"]
    end

    subgraph Launcher["Launcher"]
        AppStart["python __main__.py"]
        RegisterBlueprints["Register Blueprints"]
    end

    subgraph Config["Global Config"]
        LoadConfig["Load app_settings.json"]
    end

    subgraph API["Flask Blueprints"]
        MainBP["Main Routes"]
        CrawlerBP["Crawler API"]
        ClassifierBP["Classifier API"]
        GeneratorBP["Generation API"]
        DatabaseBP["Database CRUD"]
        DownloadBP["Download API"]
        ExampleBP["Examples"]
    end

    subgraph Crawler["Crawler Module"]
        WebCrawler["WebCrawler<br/>robots.txt<br/>Random Proxy"]
        SaveFiles["Store Raw Files"]
    end

    subgraph Processing["File Processing"]
        PDFAnalysis["PDF Text Extract"]
        PDFSplitEmbed["Chunk + Embed"]
        BM25["BM25 Term Freq"]
        SaveDB["Persist Results"]
    end

    subgraph Generation["Answer Generation"]
        RAGPipeline["RAG Pipeline"]
    end

    subgraph Database["Database Layer"]
        Models["ORM Models"]
        Ops["Query / Update"]
    end

    subgraph Logging["Logging"]
        Logger["Unified Logger"]
    end

    subgraph Storage["Persistent Data"]
        Unclassified["Raw Files"]
        DBCommon["Analysis JSON"]
        DBEmbedding["Vector Index"]
        BM25Store["BM25 term_freq"]
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

## Reference

[Project Guide(.pdf)](./STAT7008a_project.pdf)
