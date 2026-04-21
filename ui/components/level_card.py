from PySide6.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

class LevelCardWidget(QPushButton):
    level_clicked = Signal(int)

    def __init__(self, level_num: int, title: str, difficulty: str, is_locked: bool, stars_count: int = 0):
        super().__init__()
        self.level_num = level_num
        self.is_locked = is_locked
        
        self.setObjectName("level_card")
        # 🚨 تعريف خاصية ديناميكية لملف الـ QSS
        self.setProperty("locked", "true" if is_locked else "false")
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ForbiddenCursor if is_locked else Qt.CursorShape.PointingHandCursor)

        self._setup_ui(title, difficulty, stars_count)
        self._setup_accessibility(title, difficulty, stars_count)
        self.clicked.connect(self._handle_click)

    def _setup_ui(self, title: str, difficulty: str, stars_count: int):
        self.setMinimumHeight(135)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        icon_label = QLabel()
        icon_label.setObjectName("card_icon")
        icon_label.setProperty("locked", "true" if self.is_locked else "false")
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("🔒" if self.is_locked else "▶")
        layout.addWidget(icon_label)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        title_label.setProperty("locked", "true" if self.is_locked else "false")

        diff_label = QLabel(difficulty)
        diff_label.setObjectName("card_difficulty")
        diff_label.setProperty("locked", "true" if self.is_locked else "false")
        diff_label.setProperty("level", str(self.level_num))

        stars_layout = QHBoxLayout()
        stars_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        stars_layout.setSpacing(5)
        for i in range(3):
            star = QLabel("★")
            star.setObjectName("card_star")
            is_filled = "true" if (i < stars_count and not self.is_locked) else "false"
            star.setProperty("filled", is_filled)
            stars_layout.addWidget(star)
        stars_layout.addStretch()

        content_layout.addWidget(title_label)
        content_layout.addWidget(diff_label)
        content_layout.addLayout(stars_layout)

        if self.is_locked:
            lock_msg = QLabel("أكمل المستوى السابق بـ 80% لفتحه")
            lock_msg.setObjectName("card_lock_msg")
            content_layout.addWidget(lock_msg)

        layout.addLayout(content_layout)
        layout.addStretch()

    def _setup_accessibility(self, title: str, difficulty: str, stars_count: int):
        status = "مغلق" if self.is_locked else "مفتوح"
        self.setAccessibleName(f"{title}، {difficulty}. الحالة: {status}.")

    def _handle_click(self):
        if not self.is_locked:
            self.level_clicked.emit(self.level_num)
