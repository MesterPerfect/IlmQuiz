import logging
from PySide6.QtCore import QObject, Signal
from core.game_engine import GameEngine

logger = logging.getLogger(__name__)

class GameViewModel(QObject):
    """
    Acts as the bridge between the UI, GameEngine, Database, and Services.
    Handles high-level game flow and automatic triggering of audio/TTS.
    """
    
    # Signal to notify UI if an error occurs (e.g., no questions found)
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
        """Fetches all categories from the database."""
        return self.db.get_all_categories()

    def get_topics(self, category_id: int):
        """Fetches topics for a specific category."""
        return self.db.get_topics_by_category(category_id)

    def start_round(self, topic_id: int, level: int):
        """Loads questions from the database and starts the game engine."""
        questions = self.db.get_questions_by_topic_and_level(topic_id, level)
        if not questions:
            self.error_occurred.emit("No questions available for this topic and level.")
            return
            
        self.engine.load_questions(questions)
        self.engine.start_game()

    def submit_answer(self, answer_id: int):
        """Passes the selected answer ID to the game engine."""
        self.engine.check_answer(answer_id)

    def advance_game(self):
        """Moves the game to the next question."""
        self.engine.advance()

    def stop_game(self):
        """Aborts the current game and stops all media."""
        self.engine.abort_game()
        self.tts.stop()

    def read_text(self, text: str, interrupt: bool = True):
        """Helper to allow UI to trigger speech directly (e.g., for navigation)."""
        self.tts.speak(text, interrupt)

    # =========================================================
    # Internal Signal Handlers for Automated Media Feedback
    # =========================================================

    def _handle_question_changed(self, question, current_idx: int, total: int):
        """Automatically reads the question when it changes."""
        text = f"السؤال {current_idx} من {total}. {question.question}"
        self.tts.speak(text, interrupt=True)

    def _handle_time_warning(self, remaining: int):
        """Plays a warning beep. Reads the countdown for the last 3 seconds."""
        self.audio.play_sound("beep")
        if remaining <= 3:
            self.tts.speak(str(remaining), interrupt=True)

    def _handle_time_up(self):
        """Plays the time-up sound and announces it."""
        self.audio.play_sound("time_up")
        self.tts.speak("انتهى الوقت", interrupt=True)

    def _handle_answer_result(self, is_correct: bool, correct_answer):
        """Plays appropriate sound and reads the result."""
        if is_correct:
            self.audio.play_sound("correct")
            self.tts.speak("إجابة صحيحة", interrupt=True)
        else:
            self.audio.play_sound("wrong")
            self.tts.speak("إجابة خاطئة", interrupt=True)
