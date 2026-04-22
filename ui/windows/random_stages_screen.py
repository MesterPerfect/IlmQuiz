from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QPushButton, QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal

class RandomStagesScreen(QWidget):
    """Screen displaying a 100-stage journey grid for the Random Play mode."""
    
    stage_selected = Signal(int)
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.stage_buttons = []
        self._is_loaded = False  # Flag to track if buttons are already built (Lazy Loading)
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
        
        self.title_label = QLabel("الرحلة العشوائية (100 مرحلة)")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.main_layout.addLayout(header_layout)

        # Scrollable Grid (Empty initially)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("topics_scroll")
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.grid_container)
        self.main_layout.addWidget(self.scroll_area)

    def load_stages(self):
        """Builds buttons if not loaded, then updates states based on unlocked progress."""
        # ==========================================
        # 🚀 الترقيع: التحميل الكسول (Lazy Loading)
        # ==========================================
        # Only build the 100 buttons the VERY FIRST time this screen is opened
        if not self._is_loaded:
            row, col = 0, 0
            for i in range(1, 101):
                btn = QPushButton(f"مرحلة\n{i}")
                btn.setObjectName("level_button")
                btn.setFixedSize(100, 100)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked=False, stage=i: self._on_stage_clicked(stage))
                
                self.grid_layout.addWidget(btn, row, col)
                self.stage_buttons.append(btn)
                
                col += 1
                if col > 4: # 5 columns layout
                    col = 0
                    row += 1
            self._is_loaded = True
        # ==========================================

        unlocked = self.view_model.settings.get_unlocked_random_stage()
        
        for i, btn in enumerate(self.stage_buttons):
            stage_num = i + 1
            if stage_num <= unlocked:
                btn.setEnabled(True)
                btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
                btn.setText(f"مرحلة\n{stage_num}")
            else:
                btn.setEnabled(False)
                btn.setStyleSheet("background-color: #555; color: #888;")
                btn.setText("🔒")
                
        self.view_model.read_text("شاشة المراحل العشوائية.", interrupt=True)

    def _on_stage_clicked(self, stage: int):
        self.view_model.audio.play_sound("correct")
        self.stage_selected.emit(stage)
