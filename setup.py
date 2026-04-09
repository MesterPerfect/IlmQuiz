import sys
import os
import shutil
import platform
from cx_Freeze import setup, Executable

def get_platform_config():
    if sys.platform == "win32":
        return "gui", ".exe"
    return None, ""

def get_include_files():
    base_files = [("assets", "assets")]

    if sys.platform == "win32":
        if os.path.exists("UniversalSpeech"):
            base_files.append(("UniversalSpeech", "UniversalSpeech"))

    return base_files

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
    version = os.environ.get("APP_VERSION", "1.0.0")
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
        "includes": ["PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtGui", "PySide6.QtMultimedia"],
        "excludes": ["tkinter", "test", "setuptools", "pip", "numpy", "unittest"],
    }

    # Define icon path (will be applied if it exists)
    icon_path = os.path.join("assets", "icons", "app_icon.ico")
    icon_file = icon_path if sys.platform == "win32" and os.path.exists(icon_path) else None

    setup(
        name="IlmQuiz",
        version=version,
        description="IlmQuiz - Islamic Knowledge Challenge",
        author="MesterPerfect",
        options={"build_exe": build_exe_options},
        executables=[
            Executable(
                "main.py",
                base=base,
                target_name=target_name,
                icon=icon_file,
            )
        ],
    )

    clean_unused_folders(build_dir)

if __name__ == "__main__":
    main()
