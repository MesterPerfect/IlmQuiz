from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFrame, QGridLayout)
from PySide6.QtCore import Qt, Signal

class StatsScreen(QWidget):
    """Screen for displaying overall game progress and statistics."""
    
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("عودة")
        self.back_btn.setObjectName("back_button")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        self.title_label = QLabel("الإحصائيات العامة")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.main_layout.addLayout(header_layout)

        # Stats Grid
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("stats_frame") 
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setSpacing(20)
        
        self.main_layout.addWidget(self.stats_frame)
        self.main_layout.addStretch()

    def refresh_stats(self):
        """Fetches latest stats and updates the UI."""
        # Safely clear existing layout items to prevent memory leaks
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
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
            lbl.setFocusPolicy(Qt.FocusPolicy.StrongFocus) # Accessibility
            
            row = idx // 2
            col = idx % 2
            self.stats_layout.addWidget(lbl, row, col)
            
        self.view_model.read_text("شاشة الإحصائيات العامة", interrupt=True)
