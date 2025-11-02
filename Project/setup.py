"""
STAT7008A Final Group Project - 打包配置
基于 cx_Freeze 的应用打包脚本
"""

from cx_Freeze import setup, Executable
from datetime import datetime
import sys
import os
from pathlib import Path
from .global_mode import ProjectName, ProjectDescription, ProjectAuthor

# 应用信息
APP_NAME = ProjectName
APP_VERSION = f"{datetime.now().strftime('%Y.%m.%d.%H%M')}"
APP_DESCRIPTION = ProjectDescription
APP_AUTHOR = ProjectAuthor

# 主程序入口
MAIN_SCRIPT = "__main__.py"

# ========== 核心依赖包 ==========
CORE_PACKAGES = [
    # Web框架
    "flask",
    "werkzeug",
    "jinja2",
    "click",
    "itsdangerous",
    "markupsafe",
    # 异步和网络
    "aiohttp",
    "asyncio",
    "requests",
    "urllib3",
    "certifi",
    "charset_normalizer",
    "idna",
    "httpx",
    "httpcore",
    "h11",
    "anyio",
    "sniffio",
    # HTML解析
    "bs4",  # beautifulsoup4
    "soupsieve",
    "lxml",
    # 数据处理
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "joblib",
    "threadpoolctl",
    # PDF处理
    "pdfplumber",
    "pdfminer",
    "pdfminer.six",
    "PyPDF2",
    "pypdfium2",
    "fitz",  # PyMuPDF
    # 图像处理
    "PIL",  # pillow
    "opencv",
    "pytesseract",
    "albumentations",
    "albucore",
    # NLP和向量化
    "jieba",
    "nltk",
    "regex",
    # LangChain相关
    "langchain",
    "langchain_community",
    "langchain_core",
    "langchain_openai",
    "langchain_text_splitters",
    "langgraph",
    "langsmith",
    # 向量存储
    "faiss",
    # AI模型
    "transformers",
    "tokenizers",
    "torch",
    "torchvision",
    "safetensors",
    "sentence_transformers",
    "huggingface_hub",
    # API客户端
    "openai",
    "dashscope",
    # 任务调度
    "APScheduler",
    "tzlocal",
    "tzdata",
    # 数据库
    "sqlalchemy",
    "alembic",
    "flask_sqlalchemy",
    "flask_migrate",
    "greenlet",
    # 数据格式
    "json5",
    "yaml",
    "toml",
    "orjson",
    "ormsgpack",
    # 类型和验证
    "pydantic",
    "pydantic_core",
    "typing_extensions",
    "annotated_types",
    # 实用工具
    "tqdm",
    "colorama",
    "rich",
    "arrow",
    "python_dateutil",
    "filelock",
    "fsspec",
    "packaging",
    "platformdirs",
    "psutil",
    # 系统托盘
    "pystray",
    # 加密和安全
    "cryptography",
    "argon2",
    # Windows特定
    "pywin32",
    "pywin32_ctypes" if sys.platform == "win32" else None,
]

# 移除None值
CORE_PACKAGES = [pkg for pkg in CORE_PACKAGES if pkg is not None]

# ========== 排除的包（减小体积）==========
EXCLUDE_PACKAGES = [
    # 开发工具
    "unittest",
    "pytest",
    "test",
    "tests",
    # 不需要的GUI
    "tkinter",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    # Jupyter相关（如果是桌面应用不需要）
    "jupyter",
    "jupyterlab",
    "notebook",
    "ipython",
    "ipykernel",
    "ipywidgets",
    # 打包工具
    "setuptools",
    "pip",
    "wheel",
    "twine",
    "cx_Freeze",
    "pyinstaller",
    # 文档生成
    "sphinx",
    "docutils",
]

# ========== 需要包含的数据文件 ==========
INCLUDE_FILES = []

# 配置文件
config_files = [
    "app_settings.json",
]

for config_file in config_files:
    config_path = Path(config_file)
    if config_path.exists():
        INCLUDE_FILES.append((str(config_path), str(config_path)))

# 数据库目录
db_dirs = [
    "DB/BM25",
    "DB/common",
    "DB/embedding",
]

for db_dir in db_dirs:
    db_path = Path(db_dir)
    if db_path.exists():
        INCLUDE_FILES.append((str(db_path), str(db_path)))

# Resource目录
resource_dir = Path("Resource")
if resource_dir.exists():
    INCLUDE_FILES.append((str(resource_dir), "Resource"))

# ========== 构建选项 ==========
build_exe_options = {
    "packages": CORE_PACKAGES,
    "excludes": EXCLUDE_PACKAGES,
    "include_files": INCLUDE_FILES,
    "include_msvcr": True,  # 包含Microsoft Visual C++运行时
    "optimize": 2,  # 优化级别
    "build_exe": f"build/{APP_NAME}_{APP_VERSION}",  # 输出目录
}

# ========== 平台特定选项 ==========
if sys.platform == "win32":
    # Windows特定选项
    base = None  # "Win32GUI" 用于无控制台的GUI应用

    executables = [
        Executable(
            MAIN_SCRIPT,
            base=base,
            target_name=f"{APP_NAME}.exe",
            icon=None,  # 可以添加图标路径: "icon.ico"
        )
    ]

elif sys.platform == "darwin":
    # macOS特定选项
    executables = [
        Executable(
            MAIN_SCRIPT,
            target_name=APP_NAME,
        )
    ]

    build_exe_options["bundle_name"] = APP_NAME

else:
    # Linux特定选项
    executables = [
        Executable(
            MAIN_SCRIPT,
            target_name=APP_NAME.lower(),
        )
    ]

# ========== 打包配置 ==========
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={
        "build_exe": build_exe_options,
    },
    executables=executables,
)

# ========== 使用说明 ==========
"""
打包命令:
    python setup.py build

清理构建:
    python setup.py clean --all

查看帮助:
    python setup.py --help

注意事项:
1. 首次打包前确保所有依赖已安装: pip install -r requirements.txt
2. 某些包可能需要额外的数据文件,根据运行时错误调整 include_files
3. 打包后的程序在 build/ 目录下
4. 建议在目标平台上测试打包后的程序
5. 如果程序需要联网,确保防火墙允许
6. API密钥等敏感信息应通过配置文件或环境变量传递,不要硬编码

常见问题:
- 如果提示缺少DLL: 安装 Visual C++ Redistributable
- 如果模块导入失败: 检查 packages 列表是否完整
- 如果文件缺失: 检查 include_files 配置
- 如果体积过大: 调整 excludes 排除不需要的包
"""
