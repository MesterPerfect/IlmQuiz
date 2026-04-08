from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QHBoxLayout, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, Signal

class TopicsScreen(QWidget):
    """Screen displaying topics for a selected category and difficulty level selection."""
    
    topic_selected = Signal(int, int) # Emits (topic_id, level)
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.current_category_id = None
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
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        self.title_label = QLabel("اختر الموضوع ومستوى الصعوبة")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.main_layout.addLayout(header_layout)

        # Level Selection Section
        level_frame = QFrame()
        level_frame.setObjectName("level_frame")
        level_layout = QHBoxLayout(level_frame)
        
        level_label = QLabel("مستوى الصعوبة:")
        level_label.setObjectName("level_label")
        level_layout.addWidget(level_label)

        self.level_group = QButtonGroup(self)
        
        self.radio_easy = QRadioButton("سهل")
        self.radio_medium = QRadioButton("متوسط")
        self.radio_hard = QRadioButton("صعب")
        
        self.radio_easy.setChecked(True)
        
        self.level_group.addButton(self.radio_easy, 1)
        self.level_group.addButton(self.radio_medium, 2)
        self.level_group.addButton(self.radio_hard, 3)
        
        level_layout.addWidget(self.radio_easy)
        level_layout.addWidget(self.radio_medium)
        level_layout.addWidget(self.radio_hard)
        level_layout.addStretch()

        self.main_layout.addWidget(level_frame)

        # Scroll Area for Topics
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("topics_scroll")
        
        self.topics_container = QWidget()
        self.topics_layout = QGridLayout(self.topics_container)
        self.topics_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.topics_container)
        self.main_layout.addWidget(self.scroll_area)

    def load_topics(self, category_id: int):
        """Fetches topics for the given category and populates the grid."""
        self.current_category_id = category_id
        
        # Clear existing topics from the grid
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
            btn.clicked.connect(lambda checked=False, tid=topic.id: self._on_topic_clicked(tid))
            
            self.topics_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 2: # Limit to 3 columns
                col = 0
                row += 1

    def _on_topic_clicked(self, topic_id: int):
        """Handles topic selection and emits the signal with topic and chosen level."""
        self.view_model.audio.play_sound("correct")
        selected_level = self.level_group.checkedId()
        self.topic_selected.emit(topic_id, selected_level)
