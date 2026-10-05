import sys
import os
import shutil
import re
from glob import glob
from cx_Freeze import setup, Executable


def get_version():
    """Extracts the version directly from core/constants.py to avoid manual duplication."""
    constants_path = os.path.join("core", "constants.py")
    try:
        with open(constants_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'^(?:APP_)?VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Warning: Could not read version from {constants_path}. {e}")
    
    return "1.0.0"


def get_platform_config():
    if sys.platform == "win32":
        return "gui", ".exe"
    return None, ""


def get_include_files():
    # Assets folder contains sounds, database, styles, icons, and native BASS libraries
    return [("assets", "assets")]


def clean_unused_artifacts(build_dir):
    """
    Analyzes and purges bloat files and unused Qt plugins/libraries from the build output.
    Since IlmQuiz uses pure QtWidgets, SVG icons, and BASS audio via ctypes,
    all QtQuick/QML, WebEngine, QtMultimedia/FFmpeg, QtPdf, QtDesigner, and unused drivers are safely removed.
    """
    pyside_dirs = [
        os.path.join(build_dir, "lib", "PySide6"),
        os.path.join(build_dir, "lib", "PySide6", "Qt6"),
    ]

    # Directories to remove completely
    dir_names_to_remove = [
        "translations",
        "qml",
    ]

    plugin_subdirs_to_remove = [
        "sqldrivers",
        "designer",
        "multimedia",
        "qmltooling",
        "qmllint",
        "sensorgestures",
        "sensors",
        "scenegraph",
    ]

    for base in pyside_dirs:
        if not os.path.exists(base):
            continue

        for d in dir_names_to_remove:
            target = os.path.join(base, d)
            if os.path.exists(target):
                try:
                    shutil.rmtree(target, ignore_errors=True)
                    print(f"Cleaned up unused directory: {target}")
                except Exception as e:
                    print(f"Could not remove {target}: {e}")

        for p in plugin_subdirs_to_remove:
            target = os.path.join(base, "plugins", p)
            if os.path.exists(target):
                try:
                    shutil.rmtree(target, ignore_errors=True)
                    print(f"Cleaned up unused plugin directory: {target}")
                except Exception as e:
                    print(f"Could not remove {target}: {e}")

    # Patterns of large redundant files to remove
    redundant_patterns = [
        # Massive WebEngine binary (not used in IlmQuiz)
        "Qt6WebEngineCore*.dll",
        "Qt6WebEngine*.dll",
        # Unused Qt Multimedia and bundled FFmpeg DLLs (replaced by lightweight BASS)
        "Qt6Multimedia*.dll",
        "avcodec*.dll",
        "avformat*.dll",
        "avutil*.dll",
        "swresample*.dll",
        "swscale*.dll",
        # Unused QML and Quick DLLs
        "Qt6Quick*.dll",
        "Qt6Qml*.dll",
        "Qt6Labs*.dll",
        "*qml*.dll",
        # Unused PDF, Designer, VirtualKeyboard, and 3D DLLs
        "Qt6Pdf*.dll",
        "Qt6Designer*.dll",
        "Qt63D*.dll",
        "Qt6VirtualKeyboard*.dll",
        "Qt6Concurrent*.dll",
        "Qt6WebChannel*.dll",
        "Qt6UiTools*.dll",
        "Qt6Test*.dll",
        "Qt6StateMachine*.dll",
        # Software rasterizer fallback (saves ~20 MB)
        "opengl32sw.dll",
    ]

    for base in pyside_dirs:
        if not os.path.exists(base):
            continue
        for pattern in redundant_patterns:
            for match in glob(os.path.join(base, pattern)):
                try:
                    os.remove(match)
                    print(f"Removed redundant library: {os.path.basename(match)}")
                except Exception as e:
                    print(f"Could not remove {match}: {e}")


def main():
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
        "includes": [
            "PySide6.QtCore",
            "PySide6.QtWidgets",
            "PySide6.QtGui",
            "ssl",
            "urllib",
            "sqlite3",
            "packaging",
        ],
        "excludes": [
            "tkinter", "test", "setuptools", "pip", "numpy", "unittest",
            # Exclude unused Qt components to optimize distribution footprint
            "PySide6.QtNetwork",
            "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQuickControls2",
            "PySide6.QtOpenGL", "PySide6.QtOpenGLWidgets",
            "PySide6.QtSql",
            "PySide6.QtTest", "PySide6.QtPrintSupport",
            "PySide6.QtSensors", "PySide6.QtPositioning", "PySide6.QtBluetooth",
            "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtSpatialAudio",
            "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
            "PySide6.QtPdf", "PySide6.QtPdfWidgets",
            "PySide6.QtDesigner",
            "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
            "PySide6.Qt3DExtras", "PySide6.Qt3DAnimation",
            "PySide6.QtVirtualKeyboard", "PySide6.QtQuick3D",
            "PySide6.QtNfc", "PySide6.QtRemoteObjects", "PySide6.QtScxml",
        ],
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
            ),
        ],
    )

    clean_unused_artifacts(build_dir)


if __name__ == "__main__":
    main()
