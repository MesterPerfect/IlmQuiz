from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import QTimer

from .categories_screen import CategoriesScreen
from .settings_screen import SettingsScreen
from .topics_screen import TopicsScreen
from .game_screen import GameScreen


class MainWindow(QMainWindow):
    """Main application window using QStackedWidget to manage screens."""
    
    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        
        self.setWindowTitle("IlmQuiz - Islamic Knowledge Challenge")
        self.resize(1000, 750) # Adjusted size for better gameplay view
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.current_topic = None
        self.current_level = None
        
        self._init_screens()

    def _init_screens(self):
        self.categories_screen = CategoriesScreen(self.view_model)
        self.topics_screen = TopicsScreen(self.view_model)
        self.game_screen = GameScreen(self.view_model)
        self.settings_screen = SettingsScreen(self.view_model)

        # Connect signals
        self.categories_screen.category_selected.connect(self._on_category_selected)
        self.categories_screen.settings_requested.connect(self._show_settings_screen)
        self.topics_screen.back_requested.connect(self._show_categories_screen)
        self.topics_screen.topic_selected.connect(self._on_topic_selected)
        self.game_screen.game_finished.connect(self._on_game_finished)
        self.settings_screen.back_requested.connect(self._show_categories_screen)

        self.stacked_widget.addWidget(self.categories_screen)
        self.stacked_widget.addWidget(self.topics_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.settings_screen)

        self._show_categories_screen()

    def _show_settings_screen(self):
        self.stacked_widget.setCurrentWidget(self.settings_screen)
        self.view_model.read_text("شاشة الإعدادات", interrupt=True)

    def _show_categories_screen(self):
        self.stacked_widget.setCurrentWidget(self.categories_screen)
        self.view_model.read_text("شاشة التصنيفات", interrupt=True)

    def _on_category_selected(self, category_id: int):
        self.topics_screen.load_topics(category_id)
        self.stacked_widget.setCurrentWidget(self.topics_screen)
        self.view_model.read_text("شاشة المواضيع. اختر الموضوع.", interrupt=True)

    def _on_topic_selected(self, topic_id: int, level: int):
        self.current_topic = topic_id
        self.current_level = level
        
        # Ask ViewModel to load data and start engine
        self.view_model.start_round(topic_id, level)
        
        self.stacked_widget.setCurrentWidget(self.game_screen)
        self.view_model.read_text("بدأ التحدي.", interrupt=False)


    def _on_game_finished(self, score: int, max_score: int, is_win: bool):
        # Calculate number of correct answers based on points
        from core.constants import POINTS_PER_QUESTION
        correct_count = score // POINTS_PER_QUESTION
        total_questions = len(self.view_model.engine.state.questions)
        
        # Define the missing title variable
        title = "انتهت اللعبة"
        
        if is_win:
            self.view_model.audio.play_sound("correct")
            msg = f"مبروك! لقد فزت.\nلقد أجبت على {correct_count} سؤال من {total_questions}."
            
            # Unlock next level logic
            unlocked = self.view_model.settings.unlock_next_level(self.current_topic, self.current_level)
            if unlocked:
                msg += "\n\nتم فتح مستوى جديد!"
        else:
            self.view_model.audio.play_sound("wrong")
            msg = f"حظ أوفر في المرة القادمة.\nلقد أجبت على {correct_count} سؤال من {total_questions}."

        self.view_model.read_text(msg, interrupt=True)
        
        # Show message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStyleSheet("QLabel { color: white; font-size: 18px; } QPushButton { font-size: 16px; padding: 5px; }")
        msg_box.exec()
        
        # Return to topics screen after closing message box
        self.stacked_widget.setCurrentWidget(self.topics_screen)
        # Reload topics to refresh the unlock status visually
        self.topics_screen._show_levels(self.current_topic, self.topics_screen.title_label.text().replace("موضوع: ", ""))

