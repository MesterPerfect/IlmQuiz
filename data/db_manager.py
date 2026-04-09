import sqlite3
import logging
from typing import List, Optional, Tuple
from .models import Category, Topic, Question, Answer
from core.constants import DB_PATH

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> Optional[sqlite3.Connection]:
        # Connect to the SQLite database and set row factory to access columns by name
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return None

    def get_all_categories(self) -> List[Category]:
        # Retrieve all categories from the database
        categories = []
        conn = self._get_connection()
        if not conn: return categories
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories")
            rows = cursor.fetchall()
            for row in rows:
                categories.append(Category(**dict(row)))
        except sqlite3.Error as e:
            logger.error(f"Error fetching categories: {e}")
        finally:
            conn.close()
        return categories

    def get_topics_by_category(self, category_id: int) -> List[Topic]:
        # Retrieve topics filtered by category ID
        topics = []
        conn = self._get_connection()
        if not conn: return topics

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM topics WHERE category_id = ?", (category_id,))
            rows = cursor.fetchall()
            for row in rows:
                topics.append(Topic(**dict(row)))
        except sqlite3.Error as e:
            logger.error(f"Error fetching topics: {e}")
        finally:
            conn.close()
        return topics

    def get_questions_by_topic_and_level(self, topic_id: int, level: int, limit: int = 20) -> List[Question]:
        # Retrieve random questions based on topic and difficulty level
        questions = []
        conn = self._get_connection()
        if not conn: return questions

        try:
            cursor = conn.cursor()
            # Select random questions (ORDER BY RANDOM()) with the specified limit
            query = "SELECT * FROM questions WHERE topic_id = ? AND level = ? ORDER BY RANDOM() LIMIT ?"
            cursor.execute(query, (topic_id, level, limit))
            rows = cursor.fetchall()
            
            for row in rows:
                question_obj = Question(**dict(row))
                # Fetch and attach answers for each question
                question_obj.answers = self._get_answers_for_question(cursor, question_obj.id)
                questions.append(question_obj)
        except sqlite3.Error as e:
            logger.error(f"Error fetching questions: {e}")
        finally:
            conn.close()
        return questions

    def _get_answers_for_question(self, cursor: sqlite3.Cursor, question_id: str) -> List[Answer]:
        # Internal helper to fetch answers for a specific question ID
        answers = []
        try:
            cursor.execute("SELECT * FROM answers WHERE question_id = ?", (question_id,))
            rows = cursor.fetchall()
            for row in rows:
                # Convert is_correct from integer (0/1) to boolean
                data = dict(row)
                data['is_correct'] = bool(data['is_correct'])
                answers.append(Answer(**data))
        except sqlite3.Error as e:
            logger.error(f"Error fetching answers for question {question_id}: {e}")
        return answers

    def get_topic_details(self, topic_id: int) -> Tuple[str, str]:
        """
        Fetches the category name and topic name for logging purposes.
        Returns a tuple: (category_name, topic_name)
        """
        conn = self._get_connection()
        if not conn: return ("Unknown", "Unknown")

        try:
            cursor = conn.cursor()
            query = """
            SELECT c.name as cat_name, t.name as topic_name 
            FROM topics t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?
            """
            cursor.execute(query, (topic_id,))
            row = cursor.fetchone()
            if row:
                return (row['cat_name'], row['topic_name'])
        except sqlite3.Error as e:
            logger.error(f"Error fetching topic details for logging: {e}")
        finally:
            conn.close()
            
        return ("Unknown", "Unknown")
