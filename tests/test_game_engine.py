import unittest
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from data.models import Question, Answer
from core.engine.main import GameEngine
from core.engine.state import GameState

# Ensure QApplication exists for QObject / QTimer
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        
        # Sample questions
        self.answers_q1 = [
            Answer(id=1, question_id=1, answer="الإجابة الصحيحة", is_correct=True),
            Answer(id=2, question_id=1, answer="إجابة خاطئة 1", is_correct=False),
            Answer(id=3, question_id=1, answer="إجابة خاطئة 2", is_correct=False),
        ]
        self.q1 = Question(id=1, topic_id=1, level=1, question="ما هو أول أركان الإسلام؟", link="https://dorar.net", answers=self.answers_q1)

        self.answers_q2 = [
            Answer(id=4, question_id=2, answer="إجابة خاطئة", is_correct=False),
            Answer(id=5, question_id=2, answer="إجابة صحيحة 2", is_correct=True),
            Answer(id=6, question_id=2, answer="إجابة خاطئة 3", is_correct=False),
        ]
        self.q2 = Question(id=2, topic_id=1, level=1, question="كم عدد ركعات صلاة الفجر؟", link="https://dorar.net", answers=self.answers_q2)

        self.questions = [self.q1, self.q2]

    def test_load_questions(self):
        self.engine.load_questions(self.questions, "فقه", "الصلاة", level=1, time_limit=25)
        self.assertEqual(len(self.engine.state.questions), 2)
        self.assertEqual(self.engine.state.time_limit, 25)
        self.assertEqual(self.engine.state.lives, 3)
        self.assertEqual(self.engine.state.score, 0)

    def test_correct_answer(self):
        self.engine.load_questions(self.questions, "فقه", "الصلاة", level=1, time_limit=30)
        self.engine.start_game()
        
        self.assertEqual(self.engine.state.current_index, 0)
        # Select correct answer for Q1
        self.engine.check_answer(1)
        self.assertEqual(self.engine.state.score, 10)
        self.assertEqual(self.engine.state.correct_answers_count, 1)
        self.assertEqual(self.engine.state.lives, 3)

    def test_wrong_answer_reduces_lives(self):
        self.engine.load_questions(self.questions, "فقه", "الصلاة", level=1, time_limit=30)
        self.engine.start_game()
        
        # Select wrong answer for Q1
        self.engine.check_answer(2)
        self.assertEqual(self.engine.state.score, 0)
        self.assertEqual(self.engine.state.correct_answers_count, 0)
        self.assertEqual(self.engine.state.lives, 2)
        self.assertEqual(len(self.engine.state.mistakes), 1)

    def test_use_helper(self):
        self.engine.load_questions(self.questions, "فقه", "الصلاة", level=1, time_limit=30)
        self.engine.start_game()
        
        helper_result = self.engine.use_helper()
        self.assertTrue(helper_result)
        self.assertTrue(self.engine.state.helper_used)
        
        # Second call should fail
        second_helper = self.engine.use_helper()
        self.assertFalse(second_helper)

    def test_game_over_win(self):
        results = {}
        def on_game_over(stats):
            results.update(stats)
            
        self.engine.game_over.connect(on_game_over)
        self.engine.load_questions(self.questions, "فقه", "الصلاة", level=1, time_limit=30)
        self.engine.start_game()
        
        # Answer both correctly
        self.engine.check_answer(1)
        self.engine.advance()
        self.engine.check_answer(5)
        self.engine.advance()
        
        self.assertTrue(results.get("is_win", False))
        self.assertEqual(results.get("score"), 20)
        self.assertEqual(results.get("correct_count"), 2)

if __name__ == "__main__":
    unittest.main()
