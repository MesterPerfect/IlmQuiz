import sys
import logging
from PySide6.QtWidgets import QApplication

from data.db_manager import DBManager
from core.game_engine import GameEngine
from services.settings_manager import SettingsManager
from services.tts import create_tts
from services.audio_service import AudioService
from ui.view_models.game_view_model import GameViewModel
from ui.windows.main_window import MainWindow

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app_errors.log'
)

def main():
    # 1. Initialize the Qt Application
    app = QApplication(sys.argv)
    
    # 2. Initialize Services and Core Engine
    settings_manager = SettingsManager()
    db_manager = DBManager()
    tts_service = create_tts()
    audio_service = AudioService()
    game_engine = GameEngine()
    
    # 3. Initialize ViewModel (The Orchestrator)
    view_model = GameViewModel(
        settings_manager=settings_manager
        db_manager=db_manager,
        game_engine=game_engine,
        tts_service=tts_service,
        audio_service=audio_service
    )
    
    # 4. Initialize and show the Main Window
    window = MainWindow(view_model)

    # Load and apply dark theme
    try:
        with open("assets/styles/dark_theme.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logging.error(f"Failed to load theme: {e}")
    window.show()
    
    # 5. Announce startup for accessibility
    tts_service.speak("Welcome to IlmQuiz.")
    
    # 6. Execute the application loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
