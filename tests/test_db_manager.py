import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_manager import DBManager
import core.constants as const

class TestDBManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DBManager(const.DB_PATH)

    def test_database_connection_and_categories(self):
        categories = self.db.get_all_categories()
        self.assertGreaterEqual(len(categories), 6)
        arabic_names = [c.arabic_name for c in categories]
        self.assertIn("التفسير", arabic_names)
        self.assertIn("الفقه", arabic_names)

    def test_get_topics_by_category(self):
        topics = self.db.get_topics_by_category(1)
        self.assertGreater(len(topics), 0)
        self.assertEqual(topics[0].category_id, 1)

    def test_get_questions_by_topic_and_level(self):
        questions = self.db.get_questions_by_topic_and_level(topic_id=1, level=1, limit=5)
        self.assertGreater(len(questions), 0)
        for q in questions:
            self.assertEqual(len(q.answers), 3)
            # Exactly one correct answer
            correct_answers = [a for a in q.answers if a.is_correct]
            self.assertEqual(len(correct_answers), 1)

    def test_get_total_topics_count(self):
        count = self.db.get_total_topics_count()
        self.assertGreaterEqual(count, 90)

    def test_random_mixed_questions(self):
        questions = self.db.get_random_mixed_questions(limit=10, levels=[1, 2])
        self.assertEqual(len(questions), 10)
        for q in questions:
            self.assertIn(q.level, [1, 2])
            self.assertEqual(len(q.answers), 3)

if __name__ == "__main__":
    unittest.main()
