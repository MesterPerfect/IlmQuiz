from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QHBoxLayout, QStackedWidget)
from PySide6.QtCore import Qt, Signal

class TopicsScreen(QWidget):
    """Screen displaying topics, followed by a level selection view with unlock logic."""
    
    topic_selected = Signal(int, int) # Emits (topic_id, level)
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.current_category_id = None
        self.current_topic_id = None
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Header: Back Button and Title
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("عودة")
        self.back_btn.setObjectName("back_button")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self._on_back_clicked)
        
        self.title_label = QLabel("اختر الموضوع")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.main_layout.addLayout(header_layout)

        # Internal Stacked Widget for Topics -> Levels
        self.internal_stack = QStackedWidget()
        self.main_layout.addWidget(self.internal_stack)

        # View 1: Topics Scroll Area
        self.topics_view = QWidget()
        topics_vbox = QVBoxLayout(self.topics_view)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("topics_scroll")
        
        self.topics_container = QWidget()
        self.topics_layout = QGridLayout(self.topics_container)
        self.topics_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.topics_container)
        topics_vbox.addWidget(self.scroll_area)
        
        self.internal_stack.addWidget(self.topics_view)

        # View 2: Levels View
        self.levels_view = QWidget()
        levels_layout = QVBoxLayout(self.levels_view)
        levels_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        levels_layout.setSpacing(30)
        
        self.level_msg_label = QLabel("اختر مستوى الصعوبة")
        self.level_msg_label.setObjectName("level_msg_label")
        self.level_msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        levels_layout.addWidget(self.level_msg_label)

        # Level Buttons
        self.btn_easy = QPushButton("سهل")
        self.btn_medium = QPushButton("متوسط (يفتح بعد اجتياز السهل)")
        self.btn_hard = QPushButton("صعب (يفتح بعد اجتياز المتوسط)")
        
        for btn, level in [(self.btn_easy, 1), (self.btn_medium, 2), (self.btn_hard, 3)]:
            btn.setObjectName("level_button")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, l=level: self._on_level_selected(l))
            levels_layout.addWidget(btn)
            
        self.internal_stack.addWidget(self.levels_view)

    def load_topics(self, category_id: int):
        """Fetches topics for the given category and populates the grid."""
        self.current_category_id = category_id
        self.internal_stack.setCurrentWidget(self.topics_view)
        self.title_label.setText("اختر الموضوع")
        
        # Clear existing topics
        while self.topics_layout.count():
            child = self.topics_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        topics = self.view_model.get_topics(category_id)
        
        row, col = 0, 0
        for topic in topics:
            btn = QPushButton(topic.name)
            btn.setObjectName("topic_button")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, tid=topic.id, tname=topic.name: self._show_levels(tid, tname))
            
            self.topics_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _show_levels(self, topic_id: int, topic_name: str):
        """Switches to the level selection view and applies unlock logic."""
        self.current_topic_id = topic_id
        self.view_model.audio.play_sound("correct")
        self.title_label.setText(f"موضوع: {topic_name}")
        
        # Check progress from settings manager
        unlocked_level = self.view_model.settings.get_unlocked_level(topic_id)
        
        self.btn_medium.setEnabled(unlocked_level >= 2)
        self.btn_hard.setEnabled(unlocked_level >= 3)
        
        # Update text based on status
        self.btn_medium.setText("متوسط" if unlocked_level >= 2 else "متوسط (مغلق)")
        self.btn_hard.setText("صعب" if unlocked_level >= 3 else "صعب (مغلق)")
        
        self.internal_stack.setCurrentWidget(self.levels_view)
        self.view_model.read_text("اختر مستوى الصعوبة", interrupt=True)

    def _on_level_selected(self, level: int):
        self.view_model.audio.play_sound("correct")
        self.topic_selected.emit(self.current_topic_id, level)

    def _on_back_clicked(self):
        """Handles back navigation based on the current internal view."""
        if self.internal_stack.currentWidget() == self.levels_view:
            self.internal_stack.setCurrentWidget(self.topics_view)
            self.title_label.setText("اختر الموضوع")
        else:
            self.back_requested.emit()
