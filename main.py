import sys
import os
import tempfile
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLockFile
from PySide6.QtGui import QFontDatabase, QFont

from services.logger_service import setup_logging
logger = setup_logging()

import core.constants as const
from data.db_manager import DBManager
from core.engine import GameEngine
from services.settings_manager import SettingsManager
from services.tts import create_tts
from services.audio_service import AudioService
from ui.view_models.game_view_model import GameViewModel
from ui.windows.main_window import MainWindow

def main():
    # 1. Prevent multiple instances using a lock file
    lock_path = os.path.join(tempfile.gettempdir(), "ilmquiz.lock")
    lock_file = QLockFile(lock_path)
    
    # Try to lock for 100ms, if fails, another instance is running
    if not lock_file.tryLock(100):
        logger.warning("Another instance of IlmQuiz is already running. Exiting.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # 2. Load Cairo Font from assets
    font_path = os.path.join(const.BASE_DIR, "assets", "fonts", "Cairo-Regular.ttf")
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(font_family, 11))
            logger.info(f"Custom font 'Cairo' loaded and set as default.")
    else:
        logger.warning(f"Font file not found at {font_path}. Using system default.")

    # Initialize Services
    settings_manager = SettingsManager()
    db_manager = DBManager()
    audio_service = AudioService()
    game_engine = GameEngine()
    tts_service = create_tts()
    
    view_model = GameViewModel(
        db_manager=db_manager,
        game_engine=game_engine,
        tts_service=tts_service,
        audio_service=audio_service,
        settings_manager=settings_manager
    )

    view_model.apply_theme()
    window = MainWindow(view_model)
    window.show()
    
    exit_code = app.exec()
    
    if hasattr(tts_service, 'shutdown'):
        tts_service.shutdown()
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
