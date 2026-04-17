from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence


from .splash_screen import SplashScreen
from .welcome_screen import WelcomeScreen
from .document_dialog import DocumentDialog
from .categories_screen import CategoriesScreen
from .settings_screen import SettingsScreen
from ui.windows.about_screen import AboutScreen
from .stats_screen import StatsScreen 
from .random_stages_screen import RandomStagesScreen
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
        self.resize(1000, 750) 
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.current_topic = None
        self.current_level = None

        self.is_random_mode = False
        self.current_random_stage = None
        
        # --- Global Escape Key Shortcut ---
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.esc_shortcut.activated.connect(self._handle_global_escape)

        # --- Help & Changelog Shortcuts ---
        self.f1_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F1), self)
        self.f1_shortcut.activated.connect(self._show_help_dialog)
        
        self.f2_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self.f2_shortcut.activated.connect(self._show_changelog_dialog)
        # ----------------------------------
        
        self._init_screens()

    def _init_screens(self):
        # 1. Initialize all screens
        self.splash_screen = SplashScreen(self.view_model)
        self.welcome_screen = WelcomeScreen(self.view_model)
        self.categories_screen = CategoriesScreen(self.view_model)
        self.topics_screen = TopicsScreen(self.view_model)
        self.game_screen = GameScreen(self.view_model)
        self.settings_screen = SettingsScreen(self.view_model)
        self.about_screen = AboutScreen(self.view_model)
        self.stats_screen = StatsScreen(self.view_model)
        self.result_screen = ResultScreen(self.view_model)
        self.review_screen = ReviewScreen(self.view_model)
        self.random_stages_screen = RandomStagesScreen(self.view_model)

        # 2. Connect all signals
        self.splash_screen.finished.connect(self._show_welcome_screen)
        
        self.welcome_screen.start_requested.connect(self._show_categories_screen)
        self.welcome_screen.exit_requested.connect(self.close)
        
        self.categories_screen.category_selected.connect(self._on_category_selected)
        self.categories_screen.settings_requested.connect(self._show_settings_screen)
        self.categories_screen.stats_requested.connect(self._show_stats_screen)
        self.categories_screen.about_requested.connect(self._show_about_screen)
        self.categories_screen.random_requested.connect(self._show_random_stages_screen)
        
        self.topics_screen.back_requested.connect(self._show_categories_screen)
        self.topics_screen.topic_selected.connect(self._on_topic_selected)
        
        self.game_screen.back_requested.connect(self._show_categories_screen)
        self.game_screen.game_finished.connect(self._on_game_finished)
        
        self.settings_screen.back_requested.connect(self._show_categories_screen)
        self.stats_screen.back_requested.connect(self._show_categories_screen)
        self.about_screen.back_requested.connect(self._show_categories_screen)
        
        self.result_screen.retry_requested.connect(self._on_retry_requested)
        self.result_screen.back_requested.connect(self._show_categories_screen)
        self.result_screen.review_requested.connect(self._show_review_screen)
        
        self.review_screen.back_requested.connect(self._show_result_screen)

        self.random_stages_screen.back_requested.connect(self._show_categories_screen)
        self.random_stages_screen.stage_selected.connect(self._on_random_stage_selected)

        # 3. Add all screens to the stacked widget
        self.stacked_widget.addWidget(self.splash_screen)
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.categories_screen)
        self.stacked_widget.addWidget(self.topics_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.settings_screen)
        self.stacked_widget.addWidget(self.about_screen)
        self.stacked_widget.addWidget(self.stats_screen)
        self.stacked_widget.addWidget(self.result_screen)
        self.stacked_widget.addWidget(self.review_screen)
        self.stacked_widget.addWidget(self.random_stages_screen)

        self._show_splash_screen()

    # ==========================================
    # Global Navigation Handler
    # ==========================================
    def _handle_global_escape(self):
        """Smartly handles the Escape key depending on the currently active screen."""
        current_widget = self.stacked_widget.currentWidget()
        
        if current_widget == self.game_screen:
            # Game screen has a custom confirmation dialog
            current_widget._on_exit_clicked()
            
        elif current_widget == self.topics_screen:
            # Topics screen has an internal stack (Levels -> Topics)
            current_widget._on_back_clicked()
            
        elif current_widget == self.categories_screen:
            # Categories goes back to Welcome screen
            self._show_welcome_screen()
            
        elif hasattr(current_widget, 'back_requested'):
            # Settings, About, Stats, Review, Result, and Random Stages screens all use this signal
            current_widget.back_requested.emit()


    # ==========================================
    # Document Dialogs (Help & Changelog)
    # ==========================================
    def _show_help_dialog(self):
        """Opens the Help manual triggered by F1."""
        dialog = DocumentDialog(
            title="دليل مساعدة IlmQuiz", 
            filename="help.md", 
            view_model=self.view_model, 
            parent=self
        )
        dialog.exec()

    def _show_changelog_dialog(self):
        """Opens the Release Notes triggered by F2."""
        dialog = DocumentDialog(
            title="سجل التحديثات", 
            filename="changelog.md", 
            view_model=self.view_model, 
            parent=self
        )
        dialog.exec()

    # ==========================================
    # Screen Transitions
    # ==========================================
    def _show_splash_screen(self):
        self.stacked_widget.setCurrentWidget(self.splash_screen)
        self.splash_screen.start_animation()

    def _show_welcome_screen(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.view_model.read_text("شاشة الترحيب. لعبة IlmQuiz. استخدم مفتاح التبويب للتنقل.", interrupt=True)

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

    def _show_random_stages_screen(self):
        self.random_stages_screen.load_stages()
        self.stacked_widget.setCurrentWidget(self.random_stages_screen)

    def _on_category_selected(self, category_id: int):
        self.topics_screen.load_topics(category_id)
        self.stacked_widget.setCurrentWidget(self.topics_screen)
        self.view_model.read_text("شاشة المواضيع. اختر الموضوع.", interrupt=True)

    def _on_topic_selected(self, topic_id: int, level: int):
        self.is_random_mode = False
        self.current_topic = topic_id
        self.current_level = level
        
        self.view_model.start_round(topic_id, level)
        self.stacked_widget.setCurrentWidget(self.game_screen)
        self.view_model.read_text("بدأ التحدي.", interrupt=False)

    def _on_random_stage_selected(self, stage: int):
        self.is_random_mode = True
        self.current_random_stage = stage
        
        self.view_model.start_random_journey_round(stage)
        self.stacked_widget.setCurrentWidget(self.game_screen)
        self.view_model.read_text(f"بدأت المرحلة {stage}.", interrupt=False)

    def _on_retry_requested(self):
        # Support retrying for both normal and random modes
        if self.is_random_mode and self.current_random_stage is not None:
            self.view_model.start_random_journey_round(self.current_random_stage)
        elif self.current_topic is not None and self.current_level is not None:
            self.view_model.start_round(self.current_topic, self.current_level)
            
        self.stacked_widget.setCurrentWidget(self.game_screen)
        self.view_model.read_text("تم إعادة التحدي. حظاً موفقاً.", interrupt=False)

    def _on_game_finished(self, stats: dict):
        level_unlocked = False
        if stats["is_win"]:
            self.view_model.audio.play_sound("correct")
            # Unlock the proper next level/stage based on the mode
            if self.is_random_mode:
                level_unlocked = self.view_model.settings.unlock_next_random_stage(self.current_random_stage)
            else:
                level_unlocked = self.view_model.settings.unlock_next_level(self.current_topic, self.current_level)
        else:
            self.view_model.audio.play_sound("wrong")

        self.result_screen.display_results(stats, level_unlocked)
        self.stacked_widget.setCurrentWidget(self.result_screen)
        
        # Only refresh topics screen if we are in normal mode
        if not self.is_random_mode and self.current_topic is not None:
            self.topics_screen._show_levels(self.current_topic, self.topics_screen.title_label.text().replace("موضوع: ", ""))
