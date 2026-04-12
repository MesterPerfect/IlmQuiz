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
        questions = []
        conn = self._get_connection()
        if not conn: return questions

        try:
            cursor = conn.cursor()
            
            # 1. Fetch random questions within the limit
            query = "SELECT * FROM questions WHERE topic_id = ? AND level = ? ORDER BY RANDOM() LIMIT ?"
            cursor.execute(query, (topic_id, level, limit))
            rows = cursor.fetchall()
            
            if not rows:
                return questions

            # Map questions by ID for O(1) fast lookup later
            questions_dict = {}
            for row in rows:
                q_obj = Question(**dict(row))
                questions_dict[q_obj.id] = q_obj
                questions.append(q_obj)

            # 2. Extract all question IDs to fetch answers in ONE single query (Resolves N+1 Query Problem)
            question_ids = list(questions_dict.keys())
            placeholders = ",".join("?" * len(question_ids))
            
            answers_query = f"SELECT * FROM answers WHERE question_id IN ({placeholders})"
            cursor.execute(answers_query, question_ids)
            
            # Map answers to their respective questions
            for row in cursor.fetchall():
                data = dict(row)
                data['is_correct'] = bool(data['is_correct'])
                ans_obj = Answer(**data)
                
                # Append the answer safely to the correct question
                if ans_obj.question_id in questions_dict:
                    questions_dict[ans_obj.question_id].answers.append(ans_obj)
                    
        except sqlite3.Error as e:
            logger.error(f"Error fetching questions and answers: {e}")
        finally:
            conn.close()
            
        return questions

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
            SELECT c.arabic_name as cat_name, t.name as topic_name 
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


    def get_random_mixed_questions(self, limit: int = 10, levels: List[int] = [1]) -> List[Question]:
        """Fetches random questions from ANY topic, mixed by the provided difficulty levels."""
        questions = []
        conn = self._get_connection()
        if not conn: return questions

        try:
            cursor = conn.cursor()
            
            # 1. Fetch random questions across all topics matching the allowed levels
            placeholders = ",".join("?" * len(levels))
            query = f"SELECT * FROM questions WHERE level IN ({placeholders}) ORDER BY RANDOM() LIMIT ?"
            
            params = levels + [limit]
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                return questions

            # Map questions by ID for fast lookup
            questions_dict = {}
            for row in rows:
                q_obj = Question(**dict(row))
                questions_dict[q_obj.id] = q_obj
                questions.append(q_obj)

            # 2. Extract all IDs to fetch answers in ONE single query
            question_ids = list(questions_dict.keys())
            ans_placeholders = ",".join("?" * len(question_ids))
            
            answers_query = f"SELECT * FROM answers WHERE question_id IN ({ans_placeholders})"
            cursor.execute(answers_query, question_ids)
            
            # Map answers to their questions
            for row in cursor.fetchall():
                data = dict(row)
                data['is_correct'] = bool(data['is_correct'])
                ans_obj = Answer(**data)
                
                if ans_obj.question_id in questions_dict:
                    questions_dict[ans_obj.question_id].answers.append(ans_obj)
                    
        except Exception as e:
            logger.error(f"Error fetching random mixed questions: {e}")
        finally:
            conn.close()
            
        return questions
