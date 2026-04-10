from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QCheckBox, QSlider, QFrame, QMessageBox, QComboBox)
from PySide6.QtCore import Qt, Signal
import os

from services.updater import UpdateChecker
from ui.windows.update_dialog import UpdateDialog

class SettingsScreen(QWidget):
    """Screen for configuring user preferences like TTS, Volume, Logging, Updates, and Themes."""
    
    back_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.checker = None
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
        settings_layout.setSpacing(30)

        # 1. Theme Selector (ComboBox)
        theme_layout = QHBoxLayout()
        theme_label = QLabel("مظهر اللعبة (الثيم):")
        theme_label.setObjectName("settings_label")
        
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("settings_combo")
        self.theme_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_combo.addItem("الوضع الليلي (الافتراضي)", "dark_theme")
        self.theme_combo.addItem("التباين العالي (لضعاف البصر)", "high_contrast")
        self.theme_combo.currentIndexChanged.connect(self._on_settings_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        settings_layout.addLayout(theme_layout)

        # 2. TTS Toggle Checkbox
        self.tts_checkbox = QCheckBox("تفعيل الناطق الصوتي (TTS)")
        self.tts_checkbox.setObjectName("settings_checkbox")
        self.tts_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tts_checkbox.stateChanged.connect(self._on_settings_changed)
        settings_layout.addWidget(self.tts_checkbox)

        # 3. Volume Slider
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

        # 4. Logging Toggle Checkbox
        self.logging_checkbox = QCheckBox("تفعيل حفظ السجلات (Logging) للمساعدة في حل المشاكل")
        self.logging_checkbox.setObjectName("settings_checkbox")
        self.logging_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logging_checkbox.stateChanged.connect(self._on_settings_changed)
        settings_layout.addWidget(self.logging_checkbox)

        # 5. Auto Update Toggle Checkbox
        self.auto_update_checkbox = QCheckBox("البحث عن التحديثات تلقائياً عند بدء التشغيل")
        self.auto_update_checkbox.setObjectName("settings_checkbox")
        self.auto_update_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_update_checkbox.stateChanged.connect(self._on_settings_changed)
        settings_layout.addWidget(self.auto_update_checkbox)

        # 6. Manual Update Button
        self.check_update_btn = QPushButton("البحث عن تحديثات الآن")
        self.check_update_btn.setObjectName("action_button")
        self.check_update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_update_btn.setFixedSize(200, 45)
        self.check_update_btn.clicked.connect(self._manual_update_check)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.check_update_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        settings_layout.addLayout(btn_layout)

        self.main_layout.addWidget(settings_frame)
        self.main_layout.addStretch()

    def _load_current_settings(self):
        settings = self.view_model.settings.data.get("settings", {})
        tts_enabled = settings.get("tts_enabled", True)
        volume = settings.get("audio_volume", 0.8)
        logging_enabled = settings.get("logging_enabled", True)
        auto_update = settings.get("auto_update_enabled", True)
        current_theme = settings.get("theme", "dark_theme")

        self.theme_combo.blockSignals(True)
        self.tts_checkbox.blockSignals(True)
        self.volume_slider.blockSignals(True)
        self.logging_checkbox.blockSignals(True)
        self.auto_update_checkbox.blockSignals(True)

        # Set ComboBox active item based on saved theme
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.tts_checkbox.setChecked(tts_enabled)
        self.volume_slider.setValue(int(volume * 100))
        self.logging_checkbox.setChecked(logging_enabled)
        self.auto_update_checkbox.setChecked(auto_update)

        self.theme_combo.blockSignals(False)
        self.tts_checkbox.blockSignals(False)
        self.volume_slider.blockSignals(False)
        self.logging_checkbox.blockSignals(False)
        self.auto_update_checkbox.blockSignals(False)
        
        self.view_model.audio.set_volume(volume)

    def _on_settings_changed(self):
        tts_enabled = self.tts_checkbox.isChecked()
        volume = self.volume_slider.value() / 100.0
        logging_enabled = self.logging_checkbox.isChecked()
        auto_update = self.auto_update_checkbox.isChecked()
        selected_theme = self.theme_combo.currentData()
        
        self.view_model.update_all_settings(tts_enabled, volume, logging_enabled, auto_update, selected_theme)
        
        if self.sender() == self.volume_slider:
            self.view_model.audio.play_sound("beep")
            
        elif self.sender() == self.logging_checkbox:
            QMessageBox.information(self, "ملاحظة", "تغيير إعدادات السجلات سيبدأ مفعوله عند إعادة تشغيل اللعبة في المرة القادمة.")

    def _manual_update_check(self):
        self.check_update_btn.setEnabled(False)
        self.check_update_btn.setText("جاري البحث...")
        self.view_model.read_text("جاري البحث عن تحديثات.")
        
        current_version = os.environ.get("APP_VERSION", "1.0.0")
        self.checker = UpdateChecker(current_version=current_version)
        self.checker.update_available.connect(self._on_update_found)
        self.checker.no_update.connect(self._on_no_update)
        self.checker.error_occurred.connect(self._on_update_error)
        self.checker.start()

    def _on_update_found(self, version: str, notes: str, url: str):
        self._reset_update_btn()
        dialog = UpdateDialog(new_version=version, release_notes=notes, download_url=url, tts_engine=self.view_model.tts, parent=self)
        dialog.exec()

    def _on_no_update(self):
        self._reset_update_btn()
        self.view_model.read_text("أنت تستخدم أحدث إصدار.")
        QMessageBox.information(self, "تحديث", "أنت تستخدم بالفعل أحدث إصدار من اللعبة.")

    def _on_update_error(self, error_msg: str):
        self._reset_update_btn()
        self.view_model.read_text("حدث خطأ أثناء البحث عن التحديثات.")
        QMessageBox.warning(self, "خطأ", error_msg)

    def _reset_update_btn(self):
        self.check_update_btn.setEnabled(True)
        self.check_update_btn.setText("البحث عن تحديثات الآن")
