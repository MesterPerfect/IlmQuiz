import logging
import random
from PySide6.QtCore import QObject, Signal, QTimer
from typing import List

from data.models import Question
from core.constants import TIME_PER_QUESTION, POINTS_PER_QUESTION, WARNING_TIME, PASSING_SCORE
from .state import GameState

logger = logging.getLogger(__name__)

class GameEngine(QObject):
    question_changed = Signal(object, int, int)
    time_updated = Signal(int)
    time_warning = Signal(int)
    time_up = Signal()
    answer_result = Signal(bool, object)
    
    # New signals for Gamification
    game_over = Signal(int, int, bool)
    lives_changed = Signal(int)
    helper_used = Signal(int)

    def __init__(self):
        super().__init__()
        self.state = GameState()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.remaining_time = 0

    def load_questions(self, questions: List[Question]):
        self.state.reset(questions)
        logger.info(f"GameEngine loaded {len(self.state.questions)} questions.")

    def start_game(self):
        if not self.state.questions:
            logger.warning("Attempted to start game with no questions.")
            return
            
        self._next_question()
        self.lives_changed.emit(self.state.lives)

    def use_helper(self) -> bool:
        if self.state.helper_used or not self.state.current_question:
            return False
            
        current_q = self.state.current_question
        wrong_answers = [ans for ans in current_q.answers if not ans.is_correct]
        
        if wrong_answers:
            answer_to_hide = random.choice(wrong_answers)
            self.state.helper_used = True
            self.helper_used.emit(answer_to_hide.id)
            return True
            
        return False

    def check_answer(self, selected_answer_id: int):
        self.timer.stop()
        current_q = self.state.current_question
        
        if not current_q:
            return

        correct_answer = next((ans for ans in current_q.answers if ans.is_correct), None)
        is_correct = False
        
        if correct_answer and selected_answer_id == correct_answer.id:
            is_correct = True
            self.state.score += POINTS_PER_QUESTION
            self.state.correct_answers_count += 1
        else:
            self.state.lives -= 1
            self.lives_changed.emit(self.state.lives)

        self.answer_result.emit(is_correct, correct_answer)

        if self.state.lives <= 0:
            self._trigger_game_over()

    def advance(self):
        if self.state.lives > 0:
            self._next_question()

    def _next_question(self):
        self.state.current_index += 1
        
        if self.state.current_index < len(self.state.questions):
            question = self.state.current_question
            self.question_changed.emit(
                question, 
                self.state.current_index + 1, 
                len(self.state.questions)
            )
            self._reset_timer()
        else:
            self._trigger_game_over()

    def _trigger_game_over(self):
        max_score = len(self.state.questions) * POINTS_PER_QUESTION
        is_win = (self.state.correct_answers_count >= PASSING_SCORE) and (self.state.lives > 0)
        self.game_over.emit(self.state.score, max_score, is_win)

    def _reset_timer(self):
        self.remaining_time = TIME_PER_QUESTION
        self.time_updated.emit(self.remaining_time)
        self.timer.start(1000)

    def _on_timer_tick(self):
        self.remaining_time -= 1
        self.time_updated.emit(self.remaining_time)
        
        if self.remaining_time <= 0:
            self.timer.stop()
            self.time_up.emit()
            self.check_answer(-1)
        elif self.remaining_time <= WARNING_TIME:
            self.time_warning.emit(self.remaining_time)

    def abort_game(self):
        self.timer.stop()
        self.state.reset([])
