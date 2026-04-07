from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Answer:
    id: int
    question_id: str
    answer: str
    is_correct: bool

@dataclass
class Question:
    id: str
    topic_id: int
    level: int
    question: str
    link: Optional[str]
    answers: List[Answer] = None

@dataclass
class Topic:
    id: int
    category_id: int
    name: str
    slug: str

@dataclass
class Category:
    id: int
    arabic_name: str
    english_name: str
    description: str
    icon: str
