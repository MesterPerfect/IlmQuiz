import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QRadioButton, QPushButton, QButtonGroup, QFrame,
                               QProgressBar, QMessageBox, QGraphicsOpacityEffect,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)

class GameScreen(QWidget):
    """
    Main gameplay screen. Displays questions, handles answers, 
    and incorporates rich visual feedback (Animations, Glow, Shake).
    """
    game_finished = Signal(dict) 
    back_requested = Signal() 

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._animations = [] # Store animations to prevent garbage collection
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # 1. Top Bar
        self.top_bar = QHBoxLayout()
        
        self.exit_btn = QPushButton("خروج")
        self.exit_btn.setObjectName("back_button")
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self._on_exit_clicked)
        
        self.timer_label = QLabel("الوقت: 30")
        self.timer_label.setObjectName("timer_label")
        
        self.counter_label = QLabel("السؤال: 1 من 20")
        self.counter_label.setObjectName("counter_label")
        
        self.lives_label = QLabel("القلوب: ❤️❤️❤️")
        self.lives_label.setObjectName("lives_label")
        
        self.top_bar.addWidget(self.exit_btn)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.timer_label)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.counter_label)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.lives_label)
        
        self.main_layout.addLayout(self.top_bar)

        # 2. Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("game_progress_bar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setFormat("%p%") 
        self.main_layout.addWidget(self.progress_bar)

        # 3. Question Area
        self.question_label = QLabel("")
        self.question_label.setObjectName("question_label")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(self.question_label, stretch=2)

        # 4. Answers Area
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

        # 5. Bottom Bar
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

    # ==========================================
    # Animation & Effects Helpers
    # ==========================================
    def _fade_in_widget(self, widget, duration=400):
        """Applies a smooth fade-in effect to a widget."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._animations.append(anim)

    def _shake_widget(self, widget):
        """Applies a quick left-right shake effect."""
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(400)
        anim.setLoopCount(1)
        
        # Save original position
        pos = widget.pos()
        x, y = pos.x(), pos.y()
        
        anim.setKeyValueAt(0, QPoint(x, y))
        anim.setKeyValueAt(0.1, QPoint(x - 10, y))
        anim.setKeyValueAt(0.3, QPoint(x + 10, y))
        anim.setKeyValueAt(0.5, QPoint(x - 10, y))
        anim.setKeyValueAt(0.7, QPoint(x + 10, y))
        anim.setKeyValueAt(0.9, QPoint(x - 5, y))
        anim.setKeyValueAt(1.0, QPoint(x, y))
        
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._animations.append(anim)

    def _glow_widget(self, widget, color_hex):
        """Applies a glowing drop-shadow effect."""
        effect = QGraphicsDropShadowEffect(widget)
        effect.setColor(QColor(color_hex))
        effect.setBlurRadius(30)
        effect.setOffset(0, 0)
        widget.setGraphicsEffect(effect)

    def _clear_effects(self, widget):
        """Removes any graphical effects from a widget."""
        widget.setGraphicsEffect(None)

    # ==========================================
    # Event Handlers
    # ==========================================
    def _on_question_changed(self, question, current_idx, total):
        self.counter_label.setText(f"السؤال: {current_idx} من {total}")
        self.question_label.setText(question.question)
        
        percent = int((current_idx / total) * 100)
        self.progress_bar.setValue(percent)
        
        self.answer_group.setExclusive(False)
        for i, ans in enumerate(question.answers):
            rb = self.radio_buttons[i]
            rb.setText(ans.answer)
            rb.setEnabled(True)
            rb.setChecked(False)
            rb.setProperty("answer_id", ans.id)
            rb.setStyleSheet("") 
            self._clear_effects(rb) # Clear previous glow effects
        self.answer_group.setExclusive(True)
        
        self.submit_btn.setEnabled(True)
        self.helper_btn.setEnabled(not self.view_model.engine.state.helper_used)
        
        # Apply smooth fade-in transition
        self._fade_in_widget(self.question_label)
        self._fade_in_widget(self.answers_frame)

    def _on_time_updated(self, remaining):
        self.timer_label.setText(f"الوقت: {remaining}")
        # Pulse timer red if low time
        if remaining <= 5:
            self.timer_label.setStyleSheet("color: #F44336; font-weight: bold;")
        else:
            self.timer_label.setStyleSheet("")

    def _on_lives_changed(self, lives):
        hearts = "❤️" * lives
        self.lives_label.setText(f"القلوب: {hearts}")
        # Shake the lives label to emphasize the loss
        if lives < 3:
            self._shake_widget(self.lives_label)
            self._glow_widget(self.lives_label, "#F44336") # Red glow
            QTimer.singleShot(1000, lambda: self._clear_effects(self.lives_label))

    def _on_helper_clicked(self):
        self.view_model.engine.use_helper()

    def _on_helper_used(self, hidden_answer_id):
        self.helper_btn.setEnabled(False)
        self.view_model.read_text("تم حذف إجابة خاطئة.", interrupt=True)
        
        for rb in self.radio_buttons:
            if rb.property("answer_id") == hidden_answer_id:
                self._fade_in_widget(rb, duration=800) # Fade out effect visually
                rb.setEnabled(False)
                rb.setText("--- محذوف ---")
                rb.setStyleSheet("color: #555555;")
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
        checked_btn = self.answer_group.checkedButton()
        
        for rb in self.radio_buttons:
            rb.setEnabled(False) 
            
            # Highlight correct answer with Green + Glow
            if rb.property("answer_id") == correct_answer.id:
                rb.setStyleSheet("color: #4CAF50; font-weight: bold; border: 2px solid #4CAF50;") 
                self._glow_widget(rb, "#4CAF50")
                
            # Shake and mark wrong answer Red
            elif rb == checked_btn and not is_correct:
                rb.setStyleSheet("color: #F44336; text-decoration: line-through; border: 2px solid #F44336;") 
                self._shake_widget(rb)
                
        QTimer.singleShot(2500, self.view_model.advance_game)

    def _on_game_over(self, stats: dict):
        self.game_finished.emit(stats)

    def _on_exit_clicked(self):
        self.view_model.read_text("هل أنت متأكد أنك تريد الخروج؟", interrupt=True)
        reply = QMessageBox.question(
            self, "تأكيد الخروج", 
            "هل أنت متأكد أنك تريد الخروج من هذا التحدي؟\nستفقد تقدمك في هذا المستوى.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.view_model.stop_game()
            self.back_requested.emit()
            self.view_model.audio.play_sound("beep")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_T:
            remaining = self.view_model.engine.remaining_time
            self.view_model.read_text(f"الوقت المتبقي {remaining} ثانية", interrupt=True)
        elif key == Qt.Key.Key_H:
            lives = self.view_model.engine.state.lives
            lives_msg = "لديك ثلاثة قلوب" if lives == 3 else "لديك قلبان" if lives == 2 else "لديك قلب واحد" if lives == 1 else "لا يوجد لديك قلوب"
            self.view_model.read_text(lives_msg, interrupt=True)
        elif key == Qt.Key.Key_A:
            question = self.view_model.engine.state.current_question
            if question: self.view_model.read_text(question.question, interrupt=True)
        elif key == Qt.Key.Key_S:
            try:
                state = self.view_model.engine.state
                current = state.current_question_index + 1
                total = len(state.questions)
                self.view_model.read_text(f"السؤال {current} من {total}. المتبقي {total - current} أسئلة.", interrupt=True)
            except Exception: pass
        else:
            super().keyPressEvent(event)
