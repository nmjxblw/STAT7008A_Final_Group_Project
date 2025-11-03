from cv2 import log
from global_module import answer_generator_config
import log_module

logger = log_module.get_default_logger()
""" 全局日志记录器对象 """
logger.info(f"apikey_file_name: {answer_generator_config.apikey_file_name}")
