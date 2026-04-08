import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QRadioButton, QPushButton, QButtonGroup, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer

logger = logging.getLogger(__name__)

class GameScreen(QWidget):
    """
    Main gameplay screen. Displays questions, handles answers, 
    and updates the UI based on GameEngine signals.
    """
    game_finished = Signal(int, int, bool) # score, max_score, is_win

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # Top Bar: Timer, Question Counter, Lives
        self.top_bar = QHBoxLayout()
        
        self.timer_label = QLabel("الوقت: 30")
        self.timer_label.setObjectName("timer_label")
        
        self.counter_label = QLabel("السؤال: 1/20")
        self.counter_label.setObjectName("counter_label")
        
        self.lives_label = QLabel("القلوب: ❤️❤️❤️")
        self.lives_label.setObjectName("lives_label")
        
        self.top_bar.addWidget(self.timer_label)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.counter_label)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.lives_label)
        
        self.main_layout.addLayout(self.top_bar)

        # Question Area
        self.question_label = QLabel("")
        self.question_label.setObjectName("question_label")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(self.question_label, stretch=2)

        # Answers Area
        self.answers_frame = QFrame()
        self.answers_layout = QVBoxLayout(self.answers_frame)
        self.answers_layout.setSpacing(20)
        
        self.answer_group = QButtonGroup(self)
        self.radio_buttons = []
        
        for i in range(3):
            rb = QRadioButton("")
            rb.setObjectName("answer_radio")
            rb.setCursor(Qt.CursorShape.PointingHandCursor)
            self.answer_group.addButton(rb, i)
            self.answers_layout.addWidget(rb)
            self.radio_buttons.append(rb)
            
        self.main_layout.addWidget(self.answers_frame, stretch=2)

        # Bottom Bar: Helper and Submit
        self.bottom_bar = QHBoxLayout()
        
        self.helper_btn = QPushButton("مساعدة 50/50")
        self.helper_btn.setObjectName("helper_button")
        self.helper_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.helper_btn.clicked.connect(self._on_helper_clicked)
        
        self.submit_btn = QPushButton("تأكيد الإجابة")
        self.submit_btn.setObjectName("submit_button")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._on_submit_clicked)
        
        self.bottom_bar.addWidget(self.helper_btn)
        self.bottom_bar.addStretch()
        self.bottom_bar.addWidget(self.submit_btn)
        
        self.main_layout.addLayout(self.bottom_bar)

    def _connect_signals(self):
        engine = self.view_model.engine
        engine.question_changed.connect(self._on_question_changed)
        engine.time_updated.connect(self._on_time_updated)
        engine.lives_changed.connect(self._on_lives_changed)
        engine.helper_used.connect(self._on_helper_used)
        engine.answer_result.connect(self._on_answer_result)
        engine.game_over.connect(self._on_game_over)

    def _on_question_changed(self, question, current_idx, total):
        self.counter_label.setText(f"السؤال: {current_idx}/{total}")
        self.question_label.setText(question.question)
        
        # Reset radio buttons for the new question
        self.answer_group.setExclusive(False)
        for i, ans in enumerate(question.answers):
            rb = self.radio_buttons[i]
            rb.setText(ans.answer)
            rb.setEnabled(True)
            rb.setChecked(False)
            rb.setProperty("answer_id", ans.id)
            rb.setStyleSheet("") # Reset any previous styling
        self.answer_group.setExclusive(True)
        
        self.submit_btn.setEnabled(True)
        
        # Make sure helper is only enabled if not used yet
        self.helper_btn.setEnabled(not self.view_model.engine.state.helper_used)

    def _on_time_updated(self, remaining):
        self.timer_label.setText(f"الوقت: {remaining}")

    def _on_lives_changed(self, lives):
        hearts = "❤️" * lives
        self.lives_label.setText(f"القلوب: {hearts}")

    def _on_helper_clicked(self):
        self.view_model.engine.use_helper()

    def _on_helper_used(self, hidden_answer_id):
        self.helper_btn.setEnabled(False)
        self.view_model.read_text("تم حذف إجابة خاطئة.", interrupt=True)
        
        for rb in self.radio_buttons:
            if rb.property("answer_id") == hidden_answer_id:
                rb.setEnabled(False)
                rb.setText("--- محذوف ---")
                break

    def _on_submit_clicked(self):
        checked_btn = self.answer_group.checkedButton()
        if not checked_btn:
            self.view_model.read_text("الرجاء اختيار إجابة لتأكيدها.", interrupt=True)
            return
            
        self.submit_btn.setEnabled(False)
        self.helper_btn.setEnabled(False)
        
        answer_id = checked_btn.property("answer_id")
        self.view_model.submit_answer(answer_id)

    def _on_answer_result(self, is_correct, correct_answer):
        # Highlight the correct/wrong answers
        checked_btn = self.answer_group.checkedButton()
        
        for rb in self.radio_buttons:
            rb.setEnabled(False) # Disable all buttons
            if rb.property("answer_id") == correct_answer.id:
                rb.setStyleSheet("color: #4CAF50; font-weight: bold;") # Green for correct
            elif rb == checked_btn and not is_correct:
                rb.setStyleSheet("color: #F44336; text-decoration: line-through;") # Red for wrong
                
        # Wait 2.5 seconds before moving to the next question automatically
        QTimer.singleShot(2500, self.view_model.advance_game)

    def _on_game_over(self, score, max_score, is_win):
        self.game_finished.emit(score, max_score, is_win)
