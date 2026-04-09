import sys
import os
import subprocess
import logging
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

def trigger_update_installation(downloaded_file_path: str, target_version: str):
    """
    Launches the external apply_update.py script with proper arguments 
    and strictly shuts down the main application.
    """
    logger.info(f"Triggering update installation. File: {downloaded_file_path}")
    
    app = QApplication.instance()

    try:
        # Determine base directory dynamically based on current file location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.abspath(os.path.join(current_dir, "..", ".."))
        
        updater_script = os.path.join(BASE_DIR, "apply_update.py")
        
        # In a built application (PyInstaller/cx_Freeze), sys.executable is main.exe.
        # In development, it is python.exe. We need to pass the correct exe name.
        if getattr(sys, 'frozen', False):
            exe_name = os.path.basename(sys.executable)
        else:
            exe_name = "main.py" 

        # Build the argument list expected by apply_update.py
        args = [
            sys.executable, 
            updater_script,
            "--archive", downloaded_file_path,
            "--target", str(BASE_DIR),
            "--exe", exe_name
        ]
        
        # Start the updater process independently
        subprocess.Popen(args)
        logger.info("External updater launched successfully with full arguments. Exiting main application.")
        
    except Exception as e:
        logger.error(f"Failed to launch updater script: {e}")
        return

    # Quit the current instance to allow files to be overwritten
    if app:
        app.quit()
