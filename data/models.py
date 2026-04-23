from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Answer:
    id: int
    question_id: int  # Fixed: Changed from str to int to match DB schema
    answer: str
    is_correct: bool

@dataclass
class Question:
    id: int           # Fixed: Changed from str to int to match DB schema
    topic_id: int
    level: int
    question: str
    link: Optional[str]
    # Use default_factory to safely initialize an empty list instead of None
    answers: List[Answer] = field(default_factory=list)

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
