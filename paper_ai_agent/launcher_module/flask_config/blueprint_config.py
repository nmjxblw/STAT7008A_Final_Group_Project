# 配置蓝图列表： (蓝图对象, URL前缀)
blueprints = [
    (
        "launcher_module.core.flask_blueprints.main_blueprint",
        "main_bp",
        "/",
    ),
    (
        "launcher_module.core.flask_blueprints.example_blueprint",
        "example_bp",
        "/example",
    ),
]
"""蓝图配置模块"""
