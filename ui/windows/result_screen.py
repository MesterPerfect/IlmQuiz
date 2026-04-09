from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFrame, QApplication, QGridLayout)
from PySide6.QtCore import Qt, Signal

class ResultScreen(QWidget):
    """Displays the final score, stats, and provides options to share or review."""
    
    back_requested = Signal()
    review_requested = Signal(list) # Emits the list of mistakes

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.current_stats = {}
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title_label = QLabel("")
        self.title_label.setObjectName("result_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(self.title_label)

        # Stats Card
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)

        # Labels for stats
        self.score_label = QLabel("")
        self.speed_label = QLabel("")
        self.correct_label = QLabel("")
        self.wrong_label = QLabel("")
        
        for idx, lbl in enumerate([self.score_label, self.speed_label, self.correct_label, self.wrong_label]):
            lbl.setObjectName("stat_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Make label focusable for screen readers
            lbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 
            row = idx // 2
            col = idx % 2
            stats_layout.addWidget(lbl, row, col)

        self.main_layout.addWidget(stats_frame)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.btn_share = QPushButton("مشاركة النتيجة")
        self.btn_share.setObjectName("action_button")
        self.btn_share.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_share.clicked.connect(self._on_share_clicked)

        self.btn_review = QPushButton("مراجعة الأخطاء")
        self.btn_review.setObjectName("action_button")
        self.btn_review.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_review.clicked.connect(self._on_review_clicked)

        self.btn_home = QPushButton("العودة للتصنيفات")
        self.btn_home.setObjectName("action_button")
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_home.clicked.connect(self.back_requested.emit)

        buttons_layout.addWidget(self.btn_share)
        buttons_layout.addWidget(self.btn_review)
        buttons_layout.addWidget(self.btn_home)

        self.main_layout.addLayout(buttons_layout)

    def display_results(self, stats: dict, level_unlocked: bool):
        """Populates the UI with game statistics."""
        self.current_stats = stats
        
        # Set Title
        if stats["is_win"]:
            title_text = "مبروك! لقد نجحت في التحدي"
            if level_unlocked:
                title_text += "\n(تم فتح مستوى جديد)"
            self.title_label.setStyleSheet("color: #4CAF50;")
        else:
            title_text = "حظ أوفر في المرة القادمة"
            self.title_label.setStyleSheet("color: #F44336;")
            
        self.title_label.setText(title_text)

        # Set Stats
        self.score_label.setText(f"النتيجة\n{stats['score']} / {stats['max_score']}")
        self.speed_label.setText(f"متوسط السرعة\n{stats['avg_time']} ثانية/سؤال")
        self.correct_label.setText(f"إجابات صحيحة\n{stats['correct_count']}")
        self.wrong_label.setText(f"إجابات خاطئة\n{stats['wrong_count']}")

        # Show/Hide Review button
        self.btn_review.setVisible(stats["wrong_count"] > 0)

        # Accessibility announcement
        acc_text = f"{title_text}. النتيجة {stats['score']}. السرعة {stats['avg_time']} ثانية."
        self.view_model.read_text(acc_text, interrupt=True)

    def _on_share_clicked(self):
        text = (f"تحدي IlmQuiz!\n"
                f"النتيجة: {self.current_stats['score']} / {self.current_stats['max_score']}\n"
                f"متوسط السرعة: {self.current_stats['avg_time']} ثانية للسؤال.\n"
                f"هل يمكنك تحطيم رقمي؟")
        QApplication.clipboard().setText(text)
        self.view_model.audio.play_sound("correct")
        self.view_model.read_text("تم نسخ النتيجة للحافظة", interrupt=True)

    def _on_review_clicked(self):
        self.review_requested.emit(self.current_stats["mistakes"])
