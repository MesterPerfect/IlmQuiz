from typing import List, Optional
from data.models import Question

class GameState:
    def __init__(self):
        self.questions: List[Question] = []
        self.current_index: int = -1
        self.score: int = 0
        self.correct_answers_count: int = 0
        self.lives: int = 3
        self.helper_used: bool = False
        
    def reset(self, questions: List[Question]):
        self.questions = questions
        self.current_index = -1
        self.score = 0
        self.correct_answers_count = 0
        self.lives = 3
        self.helper_used = False

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
