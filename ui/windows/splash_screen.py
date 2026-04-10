import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap

class SplashScreen(QWidget):
    """
    A professional splash screen with a simple logo, fade-in animation, 
    and a startup sound. Transitions to the welcome screen automatically.
    """
    
    finished = Signal() # Signal emitted when the splash animation is over

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.animation = None
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. Logo or Title Label
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Try to load a logo if exists, otherwise use stylized text
        logo_path = os.path.join("assets", "images", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                200, 200, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("IlmQuiz")
            self.logo_label.setStyleSheet("font-size: 80px; font-weight: bold; color: #4CAF50;")
            
        # 2. Subtitle Label
        self.subtitle_label = QLabel("تحدي المعرفة الإسلامية")
        self.subtitle_label.setStyleSheet("font-size: 24px; color: #E0E0E0; margin-top: 10px;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(self.logo_label)
        self.main_layout.addWidget(self.subtitle_label)

    def start_animation(self):
        """Starts the fade-in effect and plays the startup sound."""
        # Setup Opacity Effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create Fade-in Animation (1.5 seconds)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Play startup sound (Using 'correct' if 'startup' doesn't exist yet)
        # You can add a specific 'startup.wav' to your sounds folder later
        self.view_model.audio.play_sound("startup") 
        
        self.animation.start()
        
        # Wait 3.5 seconds total (1.5s fade-in + 2s display), then finish
        QTimer.singleShot(3500, self.finished.emit)
