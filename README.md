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

For the Python interpreter, we recommend using Python version `3.13.7` or lower. The minimum version should be `3.12.0`.

```powershell
# run venv module
python3.13 -m venv .venv
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

When you see Flask indicating that it's running in PowerShell/Terminal, it means the program has successfully started. You can open the specified URL in a web browser as prompted in the terminal, usually http://127.0.0.1:8080, and you will then see a web frontend created by the program. On this webpage, you can download papers by interacting with the UI and engage with the LLM.

You can terminate the program by closing the project terminal.

## Flowchart for the Main Program

![app_flowchart](./Reference/app_flowchart.png)

## Report

[STAT7008_Project_Report(.pdf)](./Reference/STAT7008_Project_Report.pdf)

## Reference

Please goto [Reference Folder](./Reference/) to see more details about the program.
