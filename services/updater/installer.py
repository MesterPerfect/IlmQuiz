import sys
import os
import subprocess
import platform
import logging
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

def trigger_update_installation(downloaded_file_path: str, target_version: str):
    """
    Launches the external updater script (or compiled binary) with proper arguments 
    and strictly shuts down the main application to release file locks.
    """
    logger.info(f"Triggering update installation. File: {downloaded_file_path}")
    
    app = QApplication.instance()

    try:
        # Determine base directory dynamically based on current file location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            # --- COMPILED MODE (cx_Freeze) ---
            # sys.executable is the main app (IlmQuiz.exe)
            exe_name = os.path.basename(sys.executable)
            
            # Identify the correct updater binary name based on OS
            updater_name = "apply_update.exe" if platform.system() == "Windows" else "apply_update"
            updater_binary = os.path.join(BASE_DIR, updater_name)
            
            # Execute the updater binary directly
            args = [
                updater_binary,
                "--archive", downloaded_file_path,
                "--target", str(BASE_DIR),
                "--exe", exe_name
            ]
        else:
            # --- DEVELOPMENT MODE (Python Source) ---
            exe_name = "main.py"
            updater_script = os.path.join(BASE_DIR, "apply_update.py")
            
            # Execute the script using the Python interpreter
            args = [
                sys.executable, 
                updater_script,
                "--archive", downloaded_file_path,
                "--target", str(BASE_DIR),
                "--exe", exe_name
            ]
        
        # Start the updater process independently
        subprocess.Popen(args)
        logger.info("External updater launched successfully. Exiting main application.")
        
    except Exception as e:
        logger.error(f"Failed to launch updater script: {e}")
        return

    # Quit the current instance to allow files to be overwritten by the updater
    if app:
        app.quit()
