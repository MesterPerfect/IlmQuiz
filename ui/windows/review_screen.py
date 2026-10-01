from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QScrollArea, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices

class ReviewScreen(QWidget):
    """Displays questions answered incorrectly along with the correct answers and source links."""
    
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
        self.title_label = QLabel("مراجعة الأخطاء التصحيحية والمصادر")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(self.title_label)

        # Scroll Area for Mistakes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("topics_scroll") 
        
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
        """Populates the list with mistake cards and evidence links."""
        
        # Safely clear existing items, including ghost spacers (QSpacerItems)
        while self.mistakes_layout.count():
            item = self.mistakes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for idx, (question, correct_answer) in enumerate(mistakes):
            card = QFrame()
            card.setObjectName("mistake_card")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(10)
            
            q_label = QLabel(f"السؤال {idx + 1}: {question.question}")
            q_label.setObjectName("review_question")
            q_label.setWordWrap(True)
            # Make question text readable by screen readers
            q_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 
            
            ans_label = QLabel(f"الإجابة الصحيحة: {correct_answer.answer}")
            ans_label.setObjectName("review_answer")
            ans_label.setWordWrap(True)
            # Make answer text readable by screen readers
            ans_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 
            
            card_layout.addWidget(q_label)
            card_layout.addWidget(ans_label)

            # Check if source link exists for this question
            if question.link and question.link.strip():
                source_btn = QPushButton("📖 عرض الدليل والمصدر الشرعي")
                source_btn.setObjectName("action_button")
                source_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                source_btn.setStyleSheet("font-size: 14px; padding: 6px 14px; max-width: 250px; background-color: #2E7D32;")
                source_btn.setAccessibleName(f"عرض الدليل والمصدر الشرعي للسؤال رقم {idx + 1}")
                source_url = question.link.strip()
                source_btn.clicked.connect(lambda checked=False, url=source_url: self._open_source_link(url))
                
                btn_row = QHBoxLayout()
                btn_row.addWidget(source_btn)
                btn_row.addStretch()
                card_layout.addLayout(btn_row)
            
            self.mistakes_layout.addWidget(card)
            
        self.mistakes_layout.addStretch()
        self.view_model.read_text("شاشة مراجعة الأخطاء والمصادر", interrupt=True)

    def _open_source_link(self, url: str):
        """Opens reference link in user's default browser."""
        QDesktopServices.openUrl(QUrl(url))
        self.view_model.read_text("جاري فتح المصدر في المتصفح.", interrupt=True)
