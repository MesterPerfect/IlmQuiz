from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QPushButton, 
                               QLabel, QScrollArea, QHBoxLayout, QStackedWidget)
from PySide6.QtCore import Qt, Signal

# استدعاء مكون بطاقة المستويات الجديد فقط
from ui.components.level_card import LevelCardWidget

class TopicsScreen(QWidget):
    """Screen displaying topics natively, followed by a rich level selection view."""
    
    topic_selected = Signal(int, int) 
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

        # Header
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

        # Internal Stacked Widget
        self.internal_stack = QStackedWidget()
        self.main_layout.addWidget(self.internal_stack)

        # View 1: Topics Scroll Area (Original Layout)
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

        # View 2: Enhanced Levels View (With Rich Cards)
        self.levels_view = QWidget()
        self.levels_layout = QVBoxLayout(self.levels_view)
        self.levels_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.levels_layout.setSpacing(25)
        
        self.level_msg_label = QLabel("اختر مستوى الصعوبة")
        self.level_msg_label.setObjectName("level_msg_label")
        self.level_msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_msg_label.setStyleSheet("font-size: 22px; color: #FFC107; font-weight: bold;")
        self.levels_layout.addWidget(self.level_msg_label)

        self.cards_container = QVBoxLayout()
        self.cards_container.setSpacing(15)
        self.levels_layout.addLayout(self.cards_container)
        
        self.internal_stack.addWidget(self.levels_view)

    def load_topics(self, category_id: int):
        """Fetches topics and displays them using standard original buttons."""
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
            # استخدام التصميم الأصلي للأزرار بناءً على طلبك
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
        """Displays the rich interactive level cards."""
        self.current_topic_id = topic_id
        self.view_model.audio.play_sound("correct")
        self.title_label.setText(f"موضوع: {topic_name}")
        
        unlocked_level = self.view_model.settings.get_unlocked_level(topic_id)
        
        while self.cards_container.count():
            child = self.cards_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        levels_data = [
            (1, "المستوى الأول", "سهل"),
            (2, "المستوى الثاني", "متوسط"),
            (3, "المستوى الثالث", "صعب")
        ]

        for lvl_num, title, diff in levels_data:
            is_locked = lvl_num > unlocked_level
            stars = 3 if unlocked_level > lvl_num else 0
            
            # استدعاء بطاقة المستوى الجديدة
            card = LevelCardWidget(lvl_num, title, diff, is_locked, stars)
            card.level_clicked.connect(self._on_level_selected)
            self.cards_container.addWidget(card)

        self.internal_stack.setCurrentWidget(self.levels_view)
        self.view_model.read_text("اختر مستوى الصعوبة", interrupt=True)

    def _on_level_selected(self, level: int):
        self.view_model.audio.play_sound("correct")
        self.topic_selected.emit(self.current_topic_id, level)

    def _on_back_clicked(self):
        if self.internal_stack.currentWidget() == self.levels_view:
            self.internal_stack.setCurrentWidget(self.topics_view)
            self.title_label.setText("اختر الموضوع")
        else:
            self.back_requested.emit()
