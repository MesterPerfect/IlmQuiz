import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QRadioButton, 
                               QButtonGroup, QFrame, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, Signal, QTimer

# Import our newly abstracted components and effects
from ui.windows.game_screen.components import TopBarWidget, BottomBarWidget
from ui.utils.effects import apply_fade, apply_shake, apply_glow, clear_effects

logger = logging.getLogger(__name__)

class GameScreen(QWidget):
    """
    Main gameplay screen (Refactored). 
    Orchestrates the TopBar, Question Area, BottomBar, and View Model logic.
    """
    game_finished = Signal(dict) 
    back_requested = Signal() 

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # 1. Top Bar Component
        self.top_bar = TopBarWidget()
        self.top_bar.exit_requested.connect(self._on_exit_clicked)
        self.main_layout.addWidget(self.top_bar)

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
            rb.toggled.connect(lambda checked, b=rb: self._on_radio_toggled(checked, b))
            self.answer_group.addButton(rb, i)
            self.answers_layout.addWidget(rb)
            self.radio_buttons.append(rb)
            
        self.main_layout.addWidget(self.answers_frame, stretch=2)

        # 5. Bottom Bar Component
        self.bottom_bar = BottomBarWidget()
        self.bottom_bar.helper_requested.connect(self._on_helper_clicked)
        self.bottom_bar.submit_requested.connect(self._on_submit_clicked)
        self.main_layout.addWidget(self.bottom_bar)

    def _connect_signals(self):
        engine = self.view_model.engine
        engine.question_changed.connect(self._on_question_changed)
        engine.time_updated.connect(self.top_bar.update_timer)
        engine.lives_changed.connect(self.top_bar.update_lives)
        engine.helper_used.connect(self._on_helper_used)
        engine.answer_result.connect(self._on_answer_result)
        engine.game_over.connect(self._on_game_over)

    def _on_radio_toggled(self, checked, button):
        """Announces selection for screen readers when a radio button is toggled."""
        if checked:
            # We use interrupt=False to not cut off the question reading if it's still playing
            self.view_model.read_text("تم الاختيار", interrupt=False)

    # ==========================================
    # Event Handlers
    # ==========================================
    def _on_question_changed(self, question, current_idx, total):
        self.top_bar.update_counter(current_idx, total)
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
            clear_effects(rb)
        self.answer_group.setExclusive(True)
        
        self.bottom_bar.set_submit_enabled(True)
        self.bottom_bar.set_helper_enabled(not self.view_model.engine.state.helper_used)
        
        # Accessibility: Move focus to the question label automatically
        self.question_label.setFocus()

        # Apply smooth fade-in transition using the effects utility
        apply_fade(self.question_label, start=0.0, end=1.0)
        apply_fade(self.answers_frame, start=0.0, end=1.0)

    def _on_helper_clicked(self):
        self.view_model.engine.use_helper()

    def _on_helper_used(self, hidden_answer_id):
        self.bottom_bar.set_helper_enabled(False)
        self.view_model.read_text("تم حذف إجابة خاطئة.", interrupt=True)
        
        for rb in self.radio_buttons:
            if rb.property("answer_id") == hidden_answer_id:
                # Fixed Flicker Bug: Smoothly fade OUT to 30% opacity instead of restarting from 0
                apply_fade(rb, start=1.0, end=0.3, duration=800) 
                rb.setEnabled(False)
                rb.setText("--- محذوف ---")
                rb.setStyleSheet("color: #555555;")
                break

    def _on_submit_clicked(self):
        checked_btn = self.answer_group.checkedButton()
        if not checked_btn:
            self.view_model.read_text("الرجاء اختيار إجابة لتأكيدها.", interrupt=True)
            return
            
        self.bottom_bar.set_submit_enabled(False)
        self.bottom_bar.set_helper_enabled(False)
        
        answer_id = checked_btn.property("answer_id")
        self.view_model.submit_answer(answer_id)

    def _on_answer_result(self, is_correct, correct_answer):
        checked_btn = self.answer_group.checkedButton()
        
        for rb in self.radio_buttons:
            rb.setEnabled(False) 
            
            # Highlight correct answer with Green + Glow
            if rb.property("answer_id") == correct_answer.id:
                rb.setStyleSheet("color: #4CAF50; font-weight: bold; border: 2px solid #4CAF50;") 
                apply_glow(rb, "#4CAF50")
                
            # Shake and mark wrong answer Red
            elif rb == checked_btn and not is_correct:
                rb.setStyleSheet("color: #F44336; text-decoration: line-through; border: 2px solid #F44336;") 
                apply_shake(rb)
                
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
        
        # Bind Escape key to exit/back logic
        if key == Qt.Key.Key_Escape:
            self._on_exit_clicked()
            
        # Screen reader shortcuts
        elif key == Qt.Key.Key_T:
            remaining = self.view_model.engine.remaining_time
            self.view_model.read_text(f"الوقت المتبقي {remaining} ثانية", interrupt=True)
            
        elif key == Qt.Key.Key_H:
            lives = self.view_model.engine.state.lives
            lives_msg = "لديك ثلاثة قلوب" if lives == 3 else "لديك قلبان" if lives == 2 else "لديك قلب واحد" if lives == 1 else "لا يوجد لديك قلوب"
            self.view_model.read_text(lives_msg, interrupt=True)
            
        elif key == Qt.Key.Key_A:
            question = self.view_model.engine.state.current_question
            if question: 
                self.view_model.read_text(question.question, interrupt=True)
                
        elif key == Qt.Key.Key_S:
            try:
                state = self.view_model.engine.state
                current = state.current_index + 1  
                total = len(state.questions)
                self.view_model.read_text(f"السؤال {current} من {total}. المتبقي {total - current} أسئلة.", interrupt=True)
            except Exception as e: 
                logger.error(f"Shortcut S failed: {e}")
                
        else:
            # Pass unhandled keys to the parent class
            super().keyPressEvent(event)
