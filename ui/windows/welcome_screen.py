from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QApplication
from PySide6.QtCore import Qt, Signal

class WelcomeScreen(QWidget):
    """Initial screen displayed when the game launches."""
    
    start_requested = Signal()
    exit_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(40)

        # Title
        self.title_label = QLabel("IlmQuiz")
        self.title_label.setObjectName("welcome_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Subtitle
        self.subtitle_label = QLabel("تحدي المعرفة الإسلامية")
        self.subtitle_label.setObjectName("welcome_subtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Buttons Layout
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setSpacing(20)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Start Button
        self.start_btn = QPushButton("ابدأ التحدي")
        self.start_btn.setObjectName("action_button")
        self.start_btn.setFixedSize(250, 60) # Fixed size for better look
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start_clicked)

        # Exit Button
        self.exit_btn = QPushButton("خروج")
        self.exit_btn.setObjectName("action_button")
        self.exit_btn.setFixedSize(250, 60)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self.exit_requested.emit)

        self.buttons_layout.addWidget(self.start_btn)
        self.buttons_layout.addWidget(self.exit_btn)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.subtitle_label)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addStretch()

    def _on_start_clicked(self):
        # Optional: Play a sound when starting
        # self.view_model.audio.play_sound("correct") 
        self.start_requested.emit()
