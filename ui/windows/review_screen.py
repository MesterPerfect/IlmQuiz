from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal

class ReviewScreen(QWidget):
    """Displays questions answered incorrectly along with the correct answers."""
    
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Header
        self.title_label = QLabel("مراجعة الأخطاء التصحيحية")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(self.title_label)

        # Scroll Area for Mistakes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("topics_scroll") # Reuse invisible background style
        
        self.mistakes_container = QWidget()
        self.mistakes_layout = QVBoxLayout(self.mistakes_container)
        self.mistakes_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.mistakes_container)
        self.main_layout.addWidget(self.scroll_area)

        # Back Button
        self.btn_back = QPushButton("العودة للنتائج")
        self.btn_back.setObjectName("action_button")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.main_layout.addWidget(self.btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

    def load_mistakes(self, mistakes: list):
        """Populates the list with mistake cards."""
        # Clear existing items
        while self.mistakes_layout.count():
            child = self.mistakes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for idx, (question, correct_answer) in enumerate(mistakes):
            card = QFrame()
            card.setObjectName("mistake_card")
            card_layout = QVBoxLayout(card)
            
            q_label = QLabel(f"السؤال {idx + 1}: {question.question}")
            q_label.setObjectName("review_question")
            q_label.setWordWrap(True)
            
            ans_label = QLabel(f"الإجابة الصحيحة: {correct_answer.answer}")
            ans_label.setObjectName("review_answer")
            ans_label.setWordWrap(True)
            
            card_layout.addWidget(q_label)
            card_layout.addWidget(ans_label)
            
            self.mistakes_layout.addWidget(card)
            
        self.mistakes_layout.addStretch()
        self.view_model.read_text("شاشة مراجعة الأخطاء", interrupt=True)
