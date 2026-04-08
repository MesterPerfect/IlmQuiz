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
            
        self.engine.load_questions(questions)
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
