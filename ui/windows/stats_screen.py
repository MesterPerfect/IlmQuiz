from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFrame, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, Signal

class StatsScreen(QWidget):
    """Screen for displaying overall game progress, statistics, and achievement badges."""
    
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
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
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        self.title_label = QLabel("الإحصائيات والأوسمة")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.main_layout.addLayout(header_layout)

        # Scroll area for entire stats content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("topics_scroll")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(25)

        # Section 1: Stats Grid
        self.stats_title = QLabel("📊 التقدم العام في المستويات")
        self.stats_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
        self.stats_title.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.stats_title)

        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("stats_frame") 
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setSpacing(15)
        self.content_layout.addWidget(self.stats_frame)

        # Section 2: Achievements Badges Grid
        self.achievements_title = QLabel("🏆 أوسمة الإنجازات والتكريم")
        self.achievements_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFC107;")
        self.achievements_title.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(self.achievements_title)

        self.badges_frame = QFrame()
        self.badges_frame.setObjectName("stats_frame")
        self.badges_layout = QGridLayout(self.badges_frame)
        self.badges_layout.setSpacing(15)
        self.content_layout.addWidget(self.badges_frame)

        self.content_layout.addStretch()
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)

    def refresh_stats(self):
        """Fetches latest stats and achievements and updates the UI."""
        # 1. Clear Stats Grid
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. Clear Badges Grid
        while self.badges_layout.count():
            item = self.badges_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Populate Stats
        stats = self.view_model.get_global_stats()
        data = [
            ("إجمالي المواضيع", str(stats["total_topics"])),
            ("إجمالي المستويات", str(stats["total_levels"])),
            ("المستويات المكتملة", str(stats["completed_levels"])),
            ("المستويات المتبقية", str(stats["remaining_levels"]))
        ]
        
        for idx, (label_text, value_text) in enumerate(data):
            lbl = QLabel(f"{label_text}\n{value_text}")
            lbl.setObjectName("stat_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            row = idx // 2
            col = idx % 2
            self.stats_layout.addWidget(lbl, row, col)

        # Populate Achievements Badges
        achievements = self.view_model.get_achievements_status()
        for idx, ach in enumerate(achievements):
            card = QFrame()
            card.setObjectName("category_card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(6)

            title_lbl = QLabel(ach["title"])
            title_lbl.setObjectName("category_title")
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_lbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

            desc_lbl = QLabel(ach["desc"])
            desc_lbl.setObjectName("category_description")
            desc_lbl.setWordWrap(True)
            desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_lbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

            status_lbl = QLabel("✅ محقق" if ach["unlocked"] else "🔒 مقفل")
            status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_style = "color: #4CAF50; font-weight: bold;" if ach["unlocked"] else "color: #888;"
            status_lbl.setStyleSheet(status_style)
            status_lbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

            status_acc = "محقق" if ach["unlocked"] else "غير محقق حتى الآن"
            title_lbl.setAccessibleName(f"وسام {ach['title']}. {ach['desc']}. الحالة: {status_acc}.")

            if not ach["unlocked"]:
                card.setStyleSheet("opacity: 0.6; border: 1px dashed #555;")
            else:
                card.setStyleSheet("border: 1px solid #4CAF50; background-color: rgba(76, 175, 80, 0.1);")

            card_layout.addWidget(title_lbl)
            card_layout.addWidget(desc_lbl)
            card_layout.addWidget(status_lbl)

            row = idx // 2
            col = idx % 2
            self.badges_layout.addWidget(card, row, col)
            
        self.view_model.read_text("شاشة الإحصائيات والأوسمة", interrupt=True)
