import sys
import logging
import platform
import PySide6
from core.constants import LOG_FILE_PATH

def setup_logging():
    # Directory creation is now handled by core.constants
    # force=True overrides any existing empty loggers
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ],
        force=True 
    )
    
    logger = logging.getLogger("app.application")
    
    logger.info("========================================")
    logger.info("SYSTEM ENVIRONMENT INFO")
    logger.info("========================================")
    logger.info(f"OS Platform : {platform.system()} {platform.release()}")
    logger.info(f"OS Version  : {platform.version()}")
    logger.info(f"Python      : {platform.python_version()}")
    logger.info(f"PySide6     : {PySide6.__version__}")
    logger.info("========================================")
    
    return logger
