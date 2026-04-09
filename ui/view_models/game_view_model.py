import logging
from PySide6.QtCore import QObject, Signal
from core.engine import GameEngine

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

        # Connect GameEngine signals to internal handlers for audio/tts
        self.engine.time_warning.connect(self._handle_time_warning)
        self.engine.time_up.connect(self._handle_time_up)
        self.engine.answer_result.connect(self._handle_answer_result)
        self.engine.question_changed.connect(self._handle_question_changed)

    def get_categories(self):
        return self.db.get_all_categories()

    def get_topics(self, category_id: int):
        return self.db.get_topics_by_category(category_id)


    def start_round(self, topic_id: int, level: int):
        questions = self.db.get_questions_by_topic_and_level(topic_id, level)
        if not questions:
            self.error_occurred.emit("No questions available for this topic and level.")
            return
            
        # Fetch names for logging purposes
        topic = next((t for cat in self.db.get_all_categories() 
                     for t in self.db.get_topics_by_category(cat.id) 
                     if t.id == topic_id), None)
        
        category_name = "Unknown"
        topic_name = topic.name if topic else "Unknown"
        
        # If your DBManager supports getting category by topic_id directly, use it here.
        # For now, we will pass the topic name and level to the engine.
        self.engine.load_questions(questions, category_name, topic_name, level)
        self.engine.start_game()


    def submit_answer(self, answer_id: int):
        self.engine.check_answer(answer_id)

    def advance_game(self):
        self.engine.advance()

    def stop_game(self):
        self.engine.abort_game()
        self.tts.stop()

    # Add this function to save and apply settings
    def update_settings(self, tts_enabled: bool, volume: float):
        if "settings" not in self.settings.data:
            self.settings.data["settings"] = {}
            
        self.settings.data["settings"]["tts_enabled"] = tts_enabled
        self.settings.data["settings"]["audio_volume"] = volume
        self.settings.save()
        
        # Apply volume immediately to the audio service
        self.audio.set_volume(volume)

    # Update this existing function to check the settings before speaking
    def read_text(self, text: str, interrupt: bool = True):
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
