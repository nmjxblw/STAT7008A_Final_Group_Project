"""flask应用配置初始化模块"""

from .flask_config_module import *
from .blueprint_config import blueprints

__all__ = [
    "blueprints",
    "DefaultFlaskConfig",
    "DevelopmentFlaskConfig",
    "DebugFlaskConfig",
    "ProductionFlaskConfig",
]
