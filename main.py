import sys
import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# 1. Setup logging FIRST before importing other project modules
from services.logger_service import setup_logging
logger = setup_logging()

# Now import the rest of the app
from data.db_manager import DBManager
from core.engine import GameEngine
from services.settings_manager import SettingsManager
from services.tts import create_tts
from services.audio_service import AudioService
from ui.view_models.game_view_model import GameViewModel
from ui.windows.main_window import MainWindow

def main():
    logger.info("Starting IlmQuiz application...")
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    logger.info("Initializing background services and database...")
    settings_manager = SettingsManager()
    db_manager = DBManager()
    audio_service = AudioService()
    game_engine = GameEngine()
    
    logger.info("Initializing TTS service...")
    tts_service = create_tts()
    logger.info(f"Active TTS Engine class: {tts_service.__class__.__name__}")
    
    view_model = GameViewModel(
        db_manager=db_manager,
        game_engine=game_engine,
        tts_service=tts_service,
        audio_service=audio_service,
        settings_manager=settings_manager
    )

    # Apply the saved theme and dynamic font sizes globally
    view_model.apply_theme()
    
    window = MainWindow(view_model)
    window.show()
    
    exit_code = app.exec()
    
    logger.info("Application is closing. Cleaning up resources...")
    
    # Gracefully shutdown background TTS threads if applicable (Linux/macOS)
    if hasattr(tts_service, 'shutdown'):
        tts_service.shutdown()
        
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
