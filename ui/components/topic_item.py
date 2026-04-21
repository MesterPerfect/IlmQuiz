from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QStyle, QVBoxLayout
from PySide6.QtCore import Qt, Signal

class TopicItemWidget(QFrame):
    """A custom widget for topics showing progress percentage and native icons."""
    clicked = Signal(int, str)

    def __init__(self, topic_id: int, topic_name: str, unlocked_level: int, parent=None):
        super().__init__(parent)
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.unlocked_level = unlocked_level
        
        # UI setup
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("topic_item")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # 1. Status Icon (Native PySide Icons)
        self.icon_label = QLabel()
        style = self.style()
        
        if self.unlocked_level > 3: # 100% Completed
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        elif self.unlocked_level > 1: # In Progress
            icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        else: # Not started
            icon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            
        self.icon_label.setPixmap(icon.pixmap(24, 24))
        layout.addWidget(self.icon_label)

        # 2. Topic Name
        self.name_label = QLabel(self.topic_name)
        self.name_label.setObjectName("topic_item_name")
        self.name_label.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        layout.addWidget(self.name_label, 1)

        # 3. Progress Percentage Logic
        # level 1 unlocked -> 0%, level 2 -> 33%, level 3 -> 66%, level > 3 -> 100%
        if self.unlocked_level == 1:
            percentage = 0
            color = "#888888"
        elif self.unlocked_level == 2:
            percentage = 30
            color = "#FF9800"
        elif self.unlocked_level == 3:
            percentage = 66
            color = "#2196F3"
        else:
            percentage = 100
            color = "#4CAF50"

        self.progress_label = QLabel(f"{percentage}%")
        self.progress_label.setStyleSheet(f"font-size: 14px; color: {color}; font-weight: bold;")
        layout.addWidget(self.progress_label)

        # Basic interactive styling
        self.setStyleSheet("""
            QFrame#topic_item {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 5px;
            }
            QFrame#topic_item:hover, QFrame#topic_item:focus {
                background-color: #2A2A2A;
                border: 1px solid #4CAF50;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.topic_id, self.topic_name)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit(self.topic_id, self.topic_name)
        super().keyPressEvent(event)
