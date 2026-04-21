from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

class LevelCardWidget(QFrame):
    """A custom, accessible, card-based widget for level selection with rich UI."""
    level_clicked = Signal(int)

    def __init__(self, level_num: int, title: str, difficulty: str, is_locked: bool, stars_count: int = 0):
        super().__init__()
        self.level_num = level_num
        self.is_locked = is_locked
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("level_card")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ForbiddenCursor if is_locked else Qt.CursorShape.PointingHandCursor)

        self._setup_ui(title, difficulty, stars_count)
        self._setup_accessibility(title, difficulty, stars_count)

    def _setup_ui(self, title: str, difficulty: str, stars_count: int):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Left Icon
        icon_label = QLabel()
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.is_locked:
            icon_label.setText("🔒")
            icon_label.setStyleSheet("font-size: 22px; background-color: #333333; border-radius: 25px; color: #888;")
        else:
            icon_label.setText("▶")
            icon_label.setStyleSheet("font-size: 24px; color: white; background-color: #4CAF50; border-radius: 25px;")
        layout.addWidget(icon_label)

        # Center Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)

        title_label = QLabel(title)
        title_color = "#AAAAAA" if self.is_locked else "#FFFFFF"
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {title_color};")

        diff_color = "#666666" if self.is_locked else ("#4CAF50" if self.level_num == 1 else ("#FF9800" if self.level_num == 2 else "#F44336"))
        diff_label = QLabel(difficulty)
        diff_label.setStyleSheet(f"font-size: 16px; color: {diff_color};")

        stars_layout = QHBoxLayout()
        stars_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        stars_layout.setSpacing(5)
        for i in range(3):
            star = QLabel("★")
            color = "#FFD700" if i < stars_count and not self.is_locked else "#444444"
            star.setStyleSheet(f"font-size: 24px; color: {color};")
            stars_layout.addWidget(star)
        stars_layout.addStretch()

        content_layout.addWidget(title_label)
        content_layout.addWidget(diff_label)
        content_layout.addLayout(stars_layout)

        if self.is_locked:
            lock_msg = QLabel("أكمل المستوى السابق بـ 80% لفتحه")
            lock_msg.setStyleSheet("font-size: 13px; color: #F44336; margin-top: 5px;")
            content_layout.addWidget(lock_msg)

        layout.addLayout(content_layout)
        layout.addStretch()

        bg_color = "#1A1A1A" if self.is_locked else "#252528"
        border = "1px dashed #444444" if self.is_locked else "2px solid #333333"
        hover_border = "1px dashed #444444" if self.is_locked else "2px solid #4CAF50"
        
        self.setStyleSheet(f"""
            QFrame#level_card {{ background-color: {bg_color}; border: {border}; border-radius: 12px; }}
            QFrame#level_card:focus, QFrame#level_card:hover {{ border: {hover_border}; background-color: #2A2A2D; }}
        """)

    def _setup_accessibility(self, title: str, difficulty: str, stars_count: int):
        status = "مغلق" if self.is_locked else "مفتوح"
        acc_name = f"{title}، {difficulty}. الحالة: {status}."
        self.setAccessibleName(acc_name)

    def mousePressEvent(self, event):
        if not self.is_locked and event.button() == Qt.MouseButton.LeftButton:
            self.level_clicked.emit(self.level_num)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if not self.is_locked and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.level_clicked.emit(self.level_num)
        super().keyPressEvent(event)
