import os
import sys
import platform

# 1. Define App Version for CI/CD and Updaters
APP_VERSION = "1.0.4"

# 2. Determine the Base Directory (Read-only for installed apps)
IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 3. Check for Portable Mode
IS_PORTABLE = os.path.exists(os.path.join(BASE_DIR, ".portable"))

# 4. Determine User Data Directory (Read/Write permissions required for Settings & Logs)
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
# Database is Read-Only, so it safely stays in the BASE_DIR (assets) across all operating systems
DB_PATH = os.path.join(BASE_DIR, "assets", "database", "quiz.db")

SETTINGS_PATH = os.path.join(USER_DATA_DIR, "settings.json")
LOG_FILE_PATH = os.path.join(USER_DATA_DIR, "logs", "app.log")

# Assets stay in BASE_DIR because they are read-only
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")
STYLES_DIR = os.path.join(BASE_DIR, "assets", "styles")

# 6. Game Constants
DEFAULT_TIME_PER_QUESTION = 30  # Fallback time if settings are missing
WARNING_TIME = 10
POINTS_PER_QUESTION = 10
# Note: PASSING_SCORE was removed as the engine now uses dynamic percentage calculation
