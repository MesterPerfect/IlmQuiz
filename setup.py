import sys
import os
import shutil
import re
from cx_Freeze import setup, Executable

def get_version():
    """Extracts the version directly from core/constants.py to avoid manual duplication."""
    constants_path = os.path.join("core", "constants.py")
    try:
        with open(constants_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Searches for lines like: APP_VERSION = "1.0.3" or VERSION = '1.0.3'
            match = re.search(r'^(?:APP_)?VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Warning: Could not read version from {constants_path}. {e}")
    
    return "1.0.0" # Default fallback if something goes wrong

def get_platform_config():
    if sys.platform == "win32":
        return "gui", ".exe"
    return None, ""

def get_include_files():
    # Only include the actual assets folder
    return [("assets", "assets")]

def clean_unused_folders(build_dir):
    # We only remove translations. We MUST KEEP multimedia plugins for game sounds!
    folder_paths = [
        os.path.join(build_dir, "lib", "PySide6", "Qt6", "translations"),
    ]

    for folder in folder_paths:
        try:
            if os.path.exists(folder):
                shutil.rmtree(os.path.abspath(folder))
                print(f"Cleaned up: {folder}")
        except Exception as e:
            print(f"Error removing {folder}: {e}")

def main():
    # ==========================================
    # 🚀 الترقيع: قراءة الإصدار ديناميكياً
    # ==========================================
    version = get_version()
    print(f"Building IlmQuiz Version: {version}")
    
    base, ext = get_platform_config()

    target_name = f"IlmQuiz{ext}"
    
    # Output directly to dist/IlmQuiz to match the Inno Setup script
    build_dir = os.path.join("dist", "IlmQuiz")

    include_files = get_include_files()

    build_exe_options = {
        "build_exe": build_dir,
        "optimize": 2,
        "include_files": include_files,
        "packages": ["core", "data", "services", "ui"], 
        "includes": ["PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtGui", "PySide6.QtMultimedia", "ssl", "urllib"],
        "excludes": ["tkinter", "test", "setuptools", "pip", "numpy", "unittest"],
    }

    # Define icon path
    icon_path = os.path.join("assets", "icons", "app_icon.ico")
    icon_file = icon_path if sys.platform == "win32" and os.path.exists(icon_path) else None

    setup(
        name="IlmQuiz",
        version=version,
        description="IlmQuiz - Islamic Knowledge Challenge",
        author="MesterPerfect",
        options={"build_exe": build_exe_options},
        executables=[
            # 1. The Main Application
            Executable(
                "main.py",
                base=base,
                target_name=target_name,
                icon=icon_file,
            ),
            # 2. The Silent Background Updater
            Executable(
                "apply_update.py",
                base=base,
                target_name=f"apply_update{ext}",
            )
        ],
    )

    clean_unused_folders(build_dir)

if __name__ == "__main__":
    main()
