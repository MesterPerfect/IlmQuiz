import sys
import logging
import platform
import PySide6
import json
import os
from core.constants import LOG_FILE_PATH, SETTINGS_PATH, IS_PORTABLE, IS_FROZEN

def setup_logging():
    # Read settings manually to avoid circular imports during app startup
    logging_enabled = True
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging_enabled = data.get("settings", {}).get("logging_enabled", True)
        except Exception:
            pass

    # Always log to console, but conditionally log to file
    handlers = [logging.StreamHandler(sys.stdout)]
    if logging_enabled:
        handlers.append(logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8'))

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s',
        handlers=handlers,
        force=True 
    )
    
    logger = logging.getLogger("app.application")
    
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
    logger.info(f"Logging     : {'Enabled' if logging_enabled else 'Disabled (Console Only)'}")
    logger.info("========================================")
    
    return logger
