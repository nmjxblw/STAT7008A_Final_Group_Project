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
```

## Setup the Config Files

- Check and setup the [.env(.env)](./paper_ai_agent/.env) environment config file.
  - You may need to create one from [.env.example(.env.example)](./paper_ai_agent/.env.example) dotenv template file.
- Check and setup the [app_settings(.json)](./paper_ai_agent/app_settings.json) application settings json file.
- Check and setup the [app_database(.db)](./paper_ai_agent/DB/app_database.db) sqlite database file.

## Run the Project

```powershell
# set the "paper_ai_agent" as the root
cd ./paper_ai_agent
# run the launcher script
python __main__.py
```

## Flowchart and Module Description

```mermaid
graph TD
  Start[run <b>python __main__.py</b>]-->D
  A[Global Module<br>1.load dotenv file while imported<br>2.Convert app_settings.json as the Global Object,and create a singleton instance for all scripts to import.]--Setup Config-->B
  B[Log Module<br>1. Automatically creates a logging instance upon first import.<br>2. Registers a custom exception handler to prevent fatal errors from occurring without any error records.]
  C[Database Module<br>1. As a database transfer module, it automatically checks the integrity of the database and constructs the database table structure when importing the module for the first time.<br>2. Provides with interfaces for database insertion, modification, and querying.]
  D[Launcher Module<br>1. Provide program startup interface<br>2. Provide Flask-Cors instantiation function for front-end and back-end interaction.<br>3. As a data transfer module, call other module interfaces to achieve logical interaction.]
  E[Frontend Module]
  F[Crawler Module]
  Crawler[Crawler]
  HTML[Load And Display HTML Template]
  End[sys.exit]

  B--Create Instance-->Logger[Global Logger]
  D--Call Module-->A
  D--Create Instance-->Flask
  Flask--Call Module-->E--Load Resource-->HTML
  D--Call Module-->B
  D--Call Module-->C
  D--Call Module-->F--Create Instance-->Crawler
  Crawler--Do Job-->CrawlerJob1[Visit the urls]
  Crawler--Do Job-->CrawlerJob2[Extract the ]
  D--When Receive Interrupt Signal-->End
```

## Reference

[Project Guide(.pdf)](./STAT7008a_project.pdf)
