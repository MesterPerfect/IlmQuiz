import sqlite3
import logging
from typing import List, Optional
from pathlib import Path
from .models import Category, Topic, Question, Answer

# Initialize logger for database errors
logging.basicConfig(level=logging.ERROR, filename='app_errors.log')

class DBManager:
    def __init__(self, db_path: str = "data/quiz.db"):
        self.db_path = db_path

    def _get_connection(self) -> Optional[sqlite3.Connection]:
        # Connect to the SQLite database and set row factory
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return None

    def get_all_categories(self) -> List[Category]:
        # Retrieve all categories from the database
        categories = []
        conn = self._get_connection()
        if not conn:
            return categories
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories")
            rows = cursor.fetchall()
            
            # Convert SQLite rows to Category objects
            for row in rows:
                categories.append(Category(**dict(row)))
                
        except sqlite3.Error as e:
            logging.error(f"Error fetching categories: {e}")
        finally:
            conn.close()
            
        return categories
