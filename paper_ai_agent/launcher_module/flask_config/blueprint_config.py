# 配置蓝图列表： (蓝图对象, URL前缀)
blueprints = [
    # 蓝图模块路径, 蓝图对象名称, URL前缀
    # 主蓝图
    (
        "launcher_module.core.flask_blueprints.main_blueprint",
        "main_bp",
        "/",
    ),
    # 示例蓝图
    (
        "launcher_module.core.flask_blueprints.example_blueprint",
        "example_bp",
        "/example",
    ),
    # 爬虫蓝图
    (
        "launcher_module.core.flask_blueprints.crawler_blueprint",
        "crawler_bp",
        "/crawler",
    ),
    # 文件分类器蓝图
    (
        "launcher_module.core.flask_blueprints.classifier_blueprint",
        "classifier_bp",
        "/classifier",
    ),
    # 回答生成器蓝图
    (
        "launcher_module.core.flask_blueprints.generator_blueprint",
        "generator_bp",
        "/generator",
    ),
]
"""蓝图配置模块"""
