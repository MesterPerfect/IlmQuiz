from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QStyle
from PySide6.QtCore import Qt, Signal

class TopicItemWidget(QPushButton):
    clicked_topic = Signal(int, str)

    def __init__(self, topic_id: int, topic_name: str, unlocked_level: int, parent=None):
        super().__init__(parent)
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.unlocked_level = unlocked_level
        
        self.setObjectName("topic_item")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._setup_ui()
        self._setup_accessibility()
        self.clicked.connect(self._handle_click)

    def _setup_ui(self):
        self.setMinimumHeight(75)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        style = self.style()
        if self.unlocked_level > 3:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        elif self.unlocked_level > 1:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        else:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self.icon_label.setPixmap(icon.pixmap(24, 24))
        layout.addWidget(self.icon_label)

        self.name_label = QLabel(self.topic_name)
        self.name_label.setObjectName("topic_item_name")
        layout.addWidget(self.name_label, 1)

        # ==========================================
        # 🚨 الترقيع: حساب النسبة المئوية رياضياً
        # ==========================================
        MAX_LEVELS = 3
        levels_completed = min(self.unlocked_level - 1, MAX_LEVELS)
        percentage = int((levels_completed / MAX_LEVELS) * 100)

        self.progress_label = QLabel(f"{percentage}%")
        self.progress_label.setObjectName("topic_item_progress")
        self.progress_label.setProperty("level", str(self.unlocked_level))
        layout.addWidget(self.progress_label)

    def _setup_accessibility(self):
        self.setAccessibleName(f"{self.topic_name}. نسبة الإكتمال: {self.progress_label.text()}.")

    def _handle_click(self):
        self.clicked_topic.emit(self.topic_id, self.topic_name)
