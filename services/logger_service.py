import os
import sys
import logging
import platform
import PySide6

def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", "app.log")
    
    # force=True is the magic key to override any existing empty loggers
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ],
        force=True 
    )
    
    logger = logging.getLogger("app.application")
    
    # Log system environment details
    logger.info("========================================")
    logger.info("SYSTEM ENVIRONMENT INFO")
    logger.info("========================================")
    logger.info(f"OS Platform : {platform.system()} {platform.release()}")
    logger.info(f"OS Version  : {platform.version()}")
    logger.info(f"Python      : {platform.python_version()}")
    logger.info(f"PySide6     : {PySide6.__version__}")
    logger.info("========================================")
    
    return logger
