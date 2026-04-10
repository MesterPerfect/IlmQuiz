from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import QTimer

from .splash_screen import SplashScreen
from .welcome_screen import WelcomeScreen
from .categories_screen import CategoriesScreen
from .settings_screen import SettingsScreen
from ui.windows.about_screen import AboutScreen
from .stats_screen import StatsScreen 
from .topics_screen import TopicsScreen
from .game_screen import GameScreen
from .result_screen import ResultScreen
from .review_screen import ReviewScreen

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
        # Initialize the splash screen
        self.splash_screen = SplashScreen(self.view_model)
        self.welcome_screen = WelcomeScreen(self.view_model)
        self.categories_screen = CategoriesScreen(self.view_model)
        self.topics_screen = TopicsScreen(self.view_model)
        self.game_screen = GameScreen(self.view_model)
        self.settings_screen = SettingsScreen(self.view_model)
        self.about_screen = AboutScreen(self.view_model)
        self.stats_screen = StatsScreen(self.view_model)
        self.result_screen = ResultScreen(self.view_model)
        self.result_screen.retry_requested.connect(self._on_retry_requested)
        self.review_screen = ReviewScreen(self.view_model)
        self.game_screen.back_requested.connect(self._show_categories_screen)

        # Connect signals
        self.splash_screen.finished.connect(self._show_welcome_screen)
        self.welcome_screen.start_requested.connect(self._show_categories_screen)
        self.welcome_screen.exit_requested.connect(self.close) # Closes the application
        self.categories_screen.category_selected.connect(self._on_category_selected)
        self.categories_screen.settings_requested.connect(self._show_settings_screen)
        self.categories_screen.stats_requested.connect(self._show_stats_screen)
        self.categories_screen.about_requested.connect(self._show_about_screen)
        self.topics_screen.back_requested.connect(self._show_categories_screen)
        self.topics_screen.topic_selected.connect(self._on_topic_selected)
        self.game_screen.game_finished.connect(self._on_game_finished)
        self.settings_screen.back_requested.connect(self._show_categories_screen)

        
        # Result and Review signals
        self.stacked_widget.addWidget(self.splash_screen)
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stats_screen.back_requested.connect(self._show_categories_screen)
        self.result_screen.back_requested.connect(self._show_categories_screen)
        self.result_screen.review_requested.connect(self._show_review_screen)
        self.review_screen.back_requested.connect(self._show_result_screen)
        self.about_screen.back_requested.connect(self._show_categories_screen)

        self.stacked_widget.addWidget(self.categories_screen)
        self.stacked_widget.addWidget(self.topics_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.settings_screen)
        self.stacked_widget.addWidget(self.about_screen)
        self.stacked_widget.addWidget(self.stats_screen)
        self.stacked_widget.addWidget(self.result_screen)
        self.stacked_widget.addWidget(self.review_screen)

        self._show_splash_screen()

    def _show_splash_screen(self):
        self.stacked_widget.setCurrentWidget(self.splash_screen)
        self.splash_screen.start_animation()

    def _show_welcome_screen(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.view_model.read_text("شاشة الترحيب. لعبة IlmQuiz. استخدم مفتاح التبويب (Tab) للتنقل.", interrupt=True)

    def _show_settings_screen(self):
        self.stacked_widget.setCurrentWidget(self.settings_screen)
        self.view_model.read_text("شاشة الإعدادات", interrupt=True)

    def _show_about_screen(self):
        self.stacked_widget.setCurrentWidget(self.about_screen)
        self.view_model.read_text("شاشة حول البرنامج. معلومات المطور وطرق التواصل.", interrupt=True)

    def _show_stats_screen(self):
        self.stats_screen.refresh_stats()
        self.stacked_widget.setCurrentWidget(self.stats_screen)

    def _show_categories_screen(self):
        self.stacked_widget.setCurrentWidget(self.categories_screen)
        self.view_model.read_text("شاشة التصنيفات", interrupt=True)
        
    def _show_result_screen(self):
        self.stacked_widget.setCurrentWidget(self.result_screen)

    def _show_review_screen(self, mistakes):
        self.review_screen.load_mistakes(mistakes)
        self.stacked_widget.setCurrentWidget(self.review_screen)

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

    def _on_retry_requested(self):
        """Restarts the current topic and level directly."""
        if self.current_topic is not None and self.current_level is not None:
            self.view_model.start_round(self.current_topic, self.current_level)
            self.stacked_widget.setCurrentWidget(self.game_screen)
            self.view_model.read_text("تم إعادة التحدي. حظاً موفقاً.", interrupt=False)


    def _on_game_finished(self, stats: dict):
        level_unlocked = False
        if stats["is_win"]:
            self.view_model.audio.play_sound("correct")
            level_unlocked = self.view_model.settings.unlock_next_level(self.current_topic, self.current_level)
        else:
            self.view_model.audio.play_sound("wrong")

        # Pass data to result screen and show it
        self.result_screen.display_results(stats, level_unlocked)
        self.stacked_widget.setCurrentWidget(self.result_screen)
        
        # Refresh topics screen in the background to reflect new unlocked levels
        self.topics_screen._show_levels(self.current_topic, self.topics_screen.title_label.text().replace("موضوع: ", ""))