"""flask蓝图模块集合"""

from .crawler_blueprint import crawler_bp
from .example_blueprint import example_bp
from .generator_blueprint import generator_bp
from .main_blueprint import main_bp

__all__ = ["crawler_bp", "example_bp", "generator_bp", "main_bp"]
