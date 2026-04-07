import logging
from PySide6.QtCore import QObject, Signal, QTimer
from typing import List, Optional

from data.models import Question
from .constants import TIME_PER_QUESTION, POINTS_PER_QUESTION, WARNING_TIME

logger = logging.getLogger(__name__)

class GameEngine(QObject):
    """
    Core game logic manager. Handles score, current question progression, 
    and the countdown timer. Emits signals to update the UI.
    """
    
    # Signals to communicate with the UI and ViewModels
    question_changed = Signal(object, int, int)  # Question object, current index, total questions
    time_updated = Signal(int)                   # Remaining seconds
    time_warning = Signal(int)                   # Remaining seconds (triggered during the last few seconds)
    time_up = Signal()                           # Triggered when time reaches 0
    answer_result = Signal(bool, object)         # Boolean (is_correct), correct Answer object
    game_over = Signal(int, int)                 # Final score, total possible score

    def __init__(self):
        super().__init__()
        self.questions: List[Question] = []
        self.current_index: int = -1
        self.score: int = 0
        
        # Setup the game timer (triggers every 1 second)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.remaining_time: int = 0

    def load_questions(self, questions: List[Question]):
        """Loads a new set of questions and resets game state."""
        self.questions = questions
        self.current_index = -1
        self.score = 0
        logger.info(f"GameEngine loaded {len(self.questions)} questions.")

    def start_game(self):
        """Starts the game by advancing to the first question."""
        if not self.questions:
            logger.warning("Attempted to start game with no questions loaded.")
            return
            
        self.current_index = -1
        self.score = 0
        self._next_question()

    def check_answer(self, selected_answer_id: int):
        """Checks the selected answer against the correct one and stops the timer."""
        self.timer.stop()
        
        current_question = self.questions[self.current_index]
        correct_answer = next((ans for ans in current_question.answers if ans.is_correct), None)
        
        is_correct = False
        if correct_answer and selected_answer_id == correct_answer.id:
            is_correct = True
            self.score += POINTS_PER_QUESTION
            
        self.answer_result.emit(is_correct, correct_answer)

    def advance(self):
        """Moves to the next question or ends the game if no questions are left."""
        self._next_question()

    def _next_question(self):
        """Internal method to handle the progression logic."""
        self.current_index += 1
        
        if self.current_index < len(self.questions):
            # We have more questions, setup the next one
            question = self.questions[self.current_index]
            self.question_changed.emit(question, self.current_index + 1, len(self.questions))
            self._reset_timer()
        else:
            # No more questions, trigger game over
            max_score = len(self.questions) * POINTS_PER_QUESTION
            self.game_over.emit(self.score, max_score)

    def _reset_timer(self):
        """Resets and starts the countdown timer for the current question."""
        self.remaining_time = TIME_PER_QUESTION
        self.time_updated.emit(self.remaining_time)
        self.timer.start(1000)  # 1000 ms = 1 second

    def _on_timer_tick(self):
        """Handles the countdown logic triggered every second by QTimer."""
        self.remaining_time -= 1
        self.time_updated.emit(self.remaining_time)
        
        if self.remaining_time <= 0:
            self.timer.stop()
            self.time_up.emit()
            # Automatically evaluate as incorrect when time is up
            self.check_answer(-1)
        elif self.remaining_time <= WARNING_TIME:
            self.time_warning.emit(self.remaining_time)

    def abort_game(self):
        """Stops the game immediately."""
        self.timer.stop()
        self.questions.clear()
        self.current_index = -1
