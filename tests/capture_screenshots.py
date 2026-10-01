import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFontDatabase, QFont, QPixmap, QPainter

import core.constants as const
from data.db_manager import DBManager
from core.engine import GameEngine
from services.settings_manager import SettingsManager
from services.tts import create_tts
from services.audio_service import AudioService
from ui.view_models.game_view_model import GameViewModel
from ui.windows.main_window import MainWindow

def capture():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    font_path = os.path.join(const.BASE_DIR, "assets", "fonts", "Cairo-Regular.ttf")
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app.setFont(QFont(font_family, 11))

    out_dir = os.path.join(const.BASE_DIR, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    settings_manager = SettingsManager()
    db_manager = DBManager()
    audio_service = AudioService()
    game_engine = GameEngine()
    tts_service = create_tts(disable_tts=True)

    view_model = GameViewModel(
        db_manager=db_manager,
        game_engine=game_engine,
        tts_service=tts_service,
        audio_service=audio_service,
        settings_manager=settings_manager
    )

    view_model.apply_theme("dark_theme")

    window = MainWindow(view_model)
    window.resize(1000, 750)
    window.show()

    def grab_and_save(screen_name, filename):
        app.processEvents()
        pixmap = window.grab()
        file_path = os.path.join(out_dir, filename)
        pixmap.save(file_path, "PNG")
        print(f"Captured: {filename}")

    # 1. Welcome Screen
    window._show_welcome_screen()
    grab_and_save("welcome", "01_welcome.png")

    # 2. Categories Screen
    window._show_categories_screen()
    grab_and_save("categories", "02_categories.png")

    # 3. Topics Screen with Search
    window.topics_screen.load_topics(1)
    window.stacked_widget.setCurrentWidget(window.topics_screen)
    grab_and_save("topics", "03_topics_search.png")

    # 4. Game Screen
    window._on_topic_selected(1, 1)
    # Give it a moment to render question
    app.processEvents()
    grab_and_save("gameplay", "04_gameplay.png")

    # 5. Result Screen
    sample_stats = {
        "score": 90,
        "max_score": 100,
        "is_win": True,
        "correct_count": 9,
        "wrong_count": 1,
        "avg_time": 6,
        "mistakes": []
    }
    # Fetch a sample question for mistakes
    q_list = db_manager.get_questions_by_topic_and_level(1, 1, 1)
    if q_list:
        sample_stats["mistakes"] = [(q_list[0], q_list[0].answers[0])]
    
    window.result_screen.display_results(sample_stats, level_unlocked=True)
    window.stacked_widget.setCurrentWidget(window.result_screen)
    grab_and_save("result", "05_result.png")

    # 6. Review Screen
    window._show_review_screen(sample_stats["mistakes"])
    grab_and_save("review", "06_review.png")

    # 7. Stats & Badges Screen
    # Unlock a few achievements for a rich screenshot
    settings_manager.unlock_achievement("first_win")
    settings_manager.unlock_achievement("speed_demon")
    settings_manager.unlock_achievement("journey_10")
    window._show_stats_screen()
    grab_and_save("stats", "07_stats_badges.png")

    # 8. Settings Screen
    window._show_settings_screen()
    grab_and_save("settings", "08_settings.png")

    print("All screenshots generated successfully.")
    window.close()

if __name__ == "__main__":
    capture()
