import os
import logging
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from core.engine import GameEngine
import core.constants as const

logger = logging.getLogger(__name__)

class GameViewModel(QObject):
    """
    Acts as the bridge between the UI, GameEngine, Database, Settings, and Services.
    Handles high-level game flow and automatic triggering of audio/TTS.
    """
    
    error_occurred = Signal(str)

    def __init__(self, db_manager, game_engine: GameEngine, tts_service, audio_service, settings_manager):
        super().__init__()
        self.db = db_manager
        self.engine = game_engine
        self.tts = tts_service
        self.audio = audio_service
        self.settings = settings_manager

        # Connect GameEngine signals to internal handlers for audio/tts feedback
        self.engine.time_warning.connect(self._handle_time_warning)
        self.engine.time_up.connect(self._handle_time_up)
        self.engine.answer_result.connect(self._handle_answer_result)
        self.engine.question_changed.connect(self._handle_question_changed)

    def get_categories(self):
        return self.db.get_all_categories()

    def get_topics(self, category_id: int):
        return self.db.get_topics_by_category(category_id)

    def start_round(self, topic_id: int, level: int):
        # Fetch the configured time limit from settings (fallback to 30s)
        time_limit = self.settings.data.get("settings", {}).get("question_time", 30)
        
        questions = self.db.get_questions_by_topic_and_level(topic_id, level)
        if not questions:
            self.error_occurred.emit("No questions available for this topic and level.")
            return
            
        category_name, topic_name = self.db.get_topic_details(topic_id)
        
        # Pass the customized time_limit to align with the updated GameEngine signature
        self.engine.load_questions(questions, category_name, topic_name, level, time_limit)
        self.engine.start_game()

    def submit_answer(self, answer_id: int):
        self.engine.check_answer(answer_id)

    def advance_game(self):
        self.engine.advance()

    def stop_game(self):
        self.engine.abort_game()
        self.tts.stop()

    def update_all_settings(self, tts_enabled: bool, volume: float, logging_enabled: bool, auto_update_enabled: bool, theme: str, font_scale: int = 100, question_time: int = 30):
        """Updates and saves all user preferences including font scale and timer."""
        if "settings" not in self.settings.data:
            self.settings.data["settings"] = {}
            
        if hasattr(self.tts, 'enabled'):
            self.tts.enabled = tts_enabled
        self.audio.set_volume(volume)
        
        s = self.settings.data["settings"]
        s["tts_enabled"] = tts_enabled
        s["audio_volume"] = volume
        s["logging_enabled"] = logging_enabled
        s["auto_update_enabled"] = auto_update_enabled
        s["question_time"] = question_time
        s["font_scale"] = font_scale
        
        old_theme = s.get("theme", "")
        old_font = s.get("last_font_scale", 100)
        s["theme"] = theme
        s["last_font_scale"] = font_scale
        
        self.settings.save()
        
        # Apply theme instantly if theme or font size changed
        if old_theme != theme or old_font != font_scale:
            self.apply_theme(theme, font_scale)
            
        logger.info(f"Settings updated -> TTS: {tts_enabled}, Vol: {volume}, Theme: {theme}, Font: {font_scale}%, Time: {question_time}s")

    def apply_theme(self, theme_name: str = None, font_scale: int = None):
        """Loads and applies the QSS stylesheet along with dynamic font scaling."""
        if not theme_name:
            theme_name = self.settings.data.get("settings", {}).get("theme", "dark_theme")
        if not font_scale:
            font_scale = self.settings.data.get("settings", {}).get("font_scale", 100)
            
        # Use absolute base directory for safety in frozen/compiled environments
        theme_path = os.path.join(const.BASE_DIR, "assets", "styles", f"{theme_name}.qss")
        
        if os.path.exists(theme_path):
            try:
                with open(theme_path, "r", encoding="utf-8") as f:
                    qss = f.read()
                    
                    # --- DYNAMIC FONT SIZING MAGIC ---
                    scale = font_scale / 100.0
                    dynamic_qss = f"""
                    #question_label {{ font-size: {int(36 * scale)}px; }}
                    #answer_radio {{ font-size: {int(26 * scale)}px; }}
                    """
                    # ---------------------------------
                    
                    app = QApplication.instance()
                    if app:
                        app.setStyleSheet(qss + dynamic_qss) 
                
                logger.info(f"Theme '{theme_name}' applied successfully with font scale {font_scale}%.")
            except Exception as e:
                logger.error(f"Failed to load theme {theme_name}: {e}")
        else:
            logger.warning(f"Theme file not found: {theme_path}")

    def read_text(self, text: str, interrupt: bool = True):
        """Reads text aloud using TTS if enabled in settings."""
        tts_enabled = self.settings.data.get("settings", {}).get("tts_enabled", True)
        if tts_enabled:
            self.tts.speak(text, interrupt)

    # =========================================================
    # Internal Signal Handlers for Automated Media Feedback
    # =========================================================

    def _handle_question_changed(self, question, current_idx: int, total: int):
        text = f"السؤال {current_idx} من {total}. {question.question}"
        self.tts.speak(text, interrupt=True)

    def _handle_time_warning(self, remaining: int):
        self.audio.play_sound("beep")
        if remaining <= 3:
            self.tts.speak(str(remaining), interrupt=True)

    def _handle_time_up(self):
        self.audio.play_sound("time_up")
        self.tts.speak("انتهى الوقت", interrupt=True)

    def _handle_answer_result(self, is_correct: bool, correct_answer):
        if is_correct:
            self.audio.play_sound("correct")
            self.tts.speak("إجابة صحيحة", interrupt=True)
        else:
            self.audio.play_sound("wrong")
            self.tts.speak("إجابة خاطئة", interrupt=True)

    def get_global_stats(self) -> dict:
        """Calculates overall progress across all categories and topics."""
        categories = self.db.get_all_categories()
        total_topics = 0
        
        for cat in categories:
            topics = self.db.get_topics_by_category(cat.id)
            total_topics += len(topics)
            
        total_levels = total_topics * 3
        completed_levels = 0
        
        progress = self.settings.data.get("progress", {})
        for topic_id, unlocked_level in progress.items():
            # If unlocked_level is 2, it means level 1 is completed. Max is 4 (3 levels completed)
            completed = min(unlocked_level - 1, 3)
            completed_levels += completed
            
        return {
            "total_topics": total_topics,
            "total_levels": total_levels,
            "completed_levels": completed_levels,
            "remaining_levels": total_levels - completed_levels
        }


    def start_random_journey_round(self, stage: int):
        """Prepares a mixed 10-question round with dynamic difficulty based on the stage."""
        time_limit = self.settings.data.get("settings", {}).get("question_time", 30)
        
        # Dynamic Difficulty Scaling
        allowed_levels = [1] # Easy is always included
        if stage > 10:
            allowed_levels.append(2) # Introduce Medium questions after stage 10
        if stage > 30:
            allowed_levels.append(3) # Introduce Hard questions after stage 30
            
        # User requested exactly 10 questions per stage
        questions = self.db.get_random_mixed_questions(limit=10, levels=allowed_levels)
        
        if not questions:
            self.error_occurred.emit("لا توجد أسئلة كافية لبدء التحدي العشوائي.")
            return
            
        category_name = "الرحلة العشوائية"
        topic_name = f"المرحلة {stage}"
        
        self.engine.load_questions(questions, category_name, topic_name, level=0, time_limit=time_limit)
        self.engine.start_game()
