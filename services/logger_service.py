import sys
import logging
import platform
import PySide6
from core.constants import LOG_FILE_PATH, IS_PORTABLE, IS_FROZEN

def setup_logging():
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
    
    # Determine the application execution mode for accurate debugging
    if IS_PORTABLE:
        app_mode = "Portable"
    elif IS_FROZEN:
        app_mode = "Installed"
    else:
        app_mode = "Development"
    
    logger.info("========================================")
    logger.info("SYSTEM ENVIRONMENT INFO")
    logger.info("========================================")
    logger.info(f"OS Platform : {platform.system()} {platform.release()}")
    logger.info(f"OS Version  : {platform.version()}")
    logger.info(f"Python      : {platform.python_version()}")
    logger.info(f"PySide6     : {PySide6.__version__}")
    logger.info(f"App Mode    : {app_mode}")
    logger.info("========================================")
    
    return logger
