from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QCheckBox, QSlider, QFrame)
from PySide6.QtCore import Qt, Signal

class SettingsScreen(QWidget):
    """Screen for configuring user preferences like TTS and Volume."""
    
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Header layout
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("عودة")
        self.back_btn.setObjectName("back_button")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        
        self.title_label = QLabel("الإعدادات")
        self.title_label.setObjectName("screen_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label, 1)
        self.main_layout.addLayout(header_layout)

        # Settings Container
        settings_frame = QFrame()
        settings_frame.setObjectName("settings_frame")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setSpacing(40)

        # TTS Toggle Checkbox
        self.tts_checkbox = QCheckBox("تفعيل الناطق الصوتي (TTS)")
        self.tts_checkbox.setObjectName("settings_checkbox")
        self.tts_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tts_checkbox.stateChanged.connect(self._on_settings_changed)
        settings_layout.addWidget(self.tts_checkbox)

        # Volume Slider
        volume_layout = QHBoxLayout()
        volume_label = QLabel("مستوى المؤثرات الصوتية:")
        volume_label.setObjectName("settings_label")
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.volume_slider.valueChanged.connect(self._on_settings_changed)
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        
        settings_layout.addLayout(volume_layout)
        self.main_layout.addWidget(settings_frame)
        self.main_layout.addStretch()

    def _load_current_settings(self):
        # Fetch settings from the JSON manager
        settings = self.view_model.settings.data.get("settings", {})
        tts_enabled = settings.get("tts_enabled", True)
        volume = settings.get("audio_volume", 0.8)

        # Block signals temporarily to avoid saving while loading
        self.tts_checkbox.blockSignals(True)
        self.volume_slider.blockSignals(True)

        self.tts_checkbox.setChecked(tts_enabled)
        self.volume_slider.setValue(int(volume * 100))

        self.tts_checkbox.blockSignals(False)
        self.volume_slider.blockSignals(False)
        
        # Apply the initial volume to the audio service
        self.view_model.audio.set_volume(volume)

    def _on_settings_changed(self):
        # Capture UI states and pass them to the ViewModel
        tts_enabled = self.tts_checkbox.isChecked()
        volume = self.volume_slider.value() / 100.0
        self.view_model.update_settings(tts_enabled, volume)
        
        # Play a test beep when volume changes to give the user audio feedback
        if self.sender() == self.volume_slider:
            self.view_model.audio.play_sound("beep")
