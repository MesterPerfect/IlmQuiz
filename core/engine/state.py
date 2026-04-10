from typing import List, Optional, Tuple
from data.models import Question, Answer

class GameState:
    def __init__(self):
        self.questions: List[Question] = []
        self.current_index: int = -1
        self.score: int = 0
        self.correct_answers_count: int = 0
        self.lives: int = 3
        self.helper_used: bool = False
        
        # New tracking variables
        self.mistakes: List[Tuple[Question, Answer]] = []
        self.total_time_taken: int = 0
        self.answered_count: int = 0
        self.time_limit: int = 30 # Added dynamic time limit tracking
        
    def reset(self, questions: List[Question], time_limit: int = 30):
        self.questions = questions
        self.current_index = -1
        self.score = 0
        self.correct_answers_count = 0
        self.lives = 3
        self.helper_used = False
        self.mistakes.clear()
        self.total_time_taken = 0
        self.answered_count = 0
        self.time_limit = time_limit # Store the configured time limit

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
