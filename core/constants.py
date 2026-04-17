import os
import sys
import platform
import shutil

# 1. Define App Version for CI/CD and Updaters
APP_VERSION = "1.0.2"

# 2. Determine the Base Directory (Read-only for installed apps)
IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 3. Check for Portable Mode
IS_PORTABLE = os.path.exists(os.path.join(BASE_DIR, ".portable"))

# 4. Determine User Data Directory (Read/Write permissions required)
APP_NAME = "IlmQuiz"
SYSTEM_OS = platform.system()

if IS_PORTABLE or not IS_FROZEN:
    USER_DATA_DIR = BASE_DIR
else:
    if SYSTEM_OS == "Windows":
        USER_DATA_DIR = os.path.join(os.environ.get("APPDATA", ""), APP_NAME)
    elif SYSTEM_OS == "Darwin": # macOS
        USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
    else: # Linux
        USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)

# Ensure necessary directories exist
os.makedirs(os.path.join(USER_DATA_DIR, "logs"), exist_ok=True)

# 5. Define specific file paths
if IS_PORTABLE or not IS_FROZEN:
    # In portable or dev mode, deal with the database directly from assets
    DB_PATH = os.path.join(BASE_DIR, "assets", "database", "quiz.db")
else:
    # In installed mode, read from the OS config directory
    os.makedirs(os.path.join(USER_DATA_DIR, "database"), exist_ok=True)
    DB_PATH = os.path.join(USER_DATA_DIR, "database", "quiz.db")
    
    # Inno Setup handles copying on Windows safely. 
    # Python fallback is only used for Mac and Linux installations.
    if SYSTEM_OS != "Windows":
        original_db = os.path.join(BASE_DIR, "assets", "database", "quiz.db")
        if not os.path.exists(DB_PATH) and os.path.exists(original_db):
            shutil.copy2(original_db, DB_PATH)

SETTINGS_PATH = os.path.join(USER_DATA_DIR, "settings.json")
LOG_FILE_PATH = os.path.join(USER_DATA_DIR, "logs", "app.log")

# Assets stay in BASE_DIR because they are read-only
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")
STYLES_DIR = os.path.join(BASE_DIR, "assets", "styles")

# 6. Game Constants
DEFAULT_TIME_PER_QUESTION = 30  # Renamed to indicate it's a fallback
WARNING_TIME = 10
POINTS_PER_QUESTION = 10
PASSING_SCORE = 10
