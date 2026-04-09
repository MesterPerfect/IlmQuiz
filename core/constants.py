import os
import sys
import platform

# 1. Determine the Base Directory (Read-only for installed apps)
IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    # If compiled via PyInstaller, use the executable's directory
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running from source code, use the project root directory
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 2. Check for Portable Mode
# If a file named ".portable" exists next to the exe, it's portable mode
IS_PORTABLE = os.path.exists(os.path.join(BASE_DIR, ".portable"))

# 3. Determine User Data Directory (Read/Write permissions required)
APP_NAME = "IlmQuiz"

if IS_PORTABLE or not IS_FROZEN:
    # In portable mode or development, save data in the app folder
    USER_DATA_DIR = BASE_DIR
else:
    # In installed mode, use the OS-specific app data folder
    system = platform.system()
    if system == "Windows":
        USER_DATA_DIR = os.path.join(os.environ.get("APPDATA", ""), APP_NAME)
    elif system == "Darwin": # macOS
        USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
    else: # Linux
        USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)

# Ensure necessary directories exist
os.makedirs(os.path.join(USER_DATA_DIR, "database"), exist_ok=True)
os.makedirs(os.path.join(USER_DATA_DIR, "logs"), exist_ok=True)

# 4. Define specific file paths
DB_PATH = os.path.join(USER_DATA_DIR, "database", "quiz.db")
SETTINGS_PATH = os.path.join(USER_DATA_DIR, "settings.json")
LOG_FILE_PATH = os.path.join(USER_DATA_DIR, "logs", "app.log")

# Assets stay in BASE_DIR because they are read-only
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")
STYLES_DIR = os.path.join(BASE_DIR, "assets", "styles")

# 5. Game Constants
TIME_PER_QUESTION = 30
WARNING_TIME = 10
POINTS_PER_QUESTION = 10
PASSING_SCORE = 10
