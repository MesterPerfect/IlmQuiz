from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from ui.utils.effects import apply_shake, apply_glow, clear_effects
from PySide6.QtCore import QTimer

class TopBarWidget(QWidget):
    """Manages the top bar of the game screen (Timer, Counter, Lives, Exit)."""
    exit_requested = Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.exit_btn = QPushButton("خروج")
        self.exit_btn.setObjectName("back_button")
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self.exit_requested.emit)
        
        self.timer_label = QLabel("الوقت: --")
        self.timer_label.setObjectName("timer_label")
        
        self.counter_label = QLabel("السؤال: --")
        self.counter_label.setObjectName("counter_label")
        
        self.lives_label = QLabel("القلوب: ❤️❤️❤️")
        self.lives_label.setObjectName("lives_label")
        
        layout.addWidget(self.exit_btn)
        layout.addStretch()
        layout.addWidget(self.timer_label)
        layout.addStretch()
        layout.addWidget(self.counter_label)
        layout.addStretch()
        layout.addWidget(self.lives_label)

    def update_timer(self, remaining: int):
        self.timer_label.setText(f"الوقت: {remaining}")
        if remaining <= 5:
            self.timer_label.setStyleSheet("color: #F44336; font-weight: bold;")
        else:
            self.timer_label.setStyleSheet("")

    def update_counter(self, current: int, total: int):
        self.counter_label.setText(f"السؤال: {current} من {total}")

    def update_lives(self, lives: int):
        hearts = "❤️" * lives
        self.lives_label.setText(f"القلوب: {hearts}")
        if lives < 3:
            apply_shake(self.lives_label)
            apply_glow(self.lives_label, "#F44336")
            QTimer.singleShot(1000, lambda: clear_effects(self.lives_label))


class BottomBarWidget(QWidget):
    """Manages the bottom action buttons (Helper, Submit)."""
    helper_requested = Signal()
    submit_requested = Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.helper_btn = QPushButton("مساعدة 50/50")
        self.helper_btn.setObjectName("helper_button")
        self.helper_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.helper_btn.clicked.connect(self.helper_requested.emit)
        
        self.submit_btn = QPushButton("تأكيد الإجابة")
        self.submit_btn.setObjectName("submit_button")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self.submit_requested.emit)
        
        layout.addWidget(self.helper_btn)
        layout.addStretch()
        layout.addWidget(self.submit_btn)

    def set_helper_enabled(self, enabled: bool):
        self.helper_btn.setEnabled(enabled)

    def set_submit_enabled(self, enabled: bool):
        self.submit_btn.setEnabled(enabled)
