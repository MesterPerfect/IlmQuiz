import os
import core.constants as const
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QApplication
from PySide6.QtCore import Qt, Signal

from services.updater import UpdateChecker
from ui.windows.update_dialog import UpdateDialog

class WelcomeScreen(QWidget):
    """Initial screen displayed when the game launches."""
    
    start_requested = Signal()
    exit_requested = Signal()

    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.checker = None
        self._has_checked_updates = False  # Track if we already checked
        self._setup_ui()
        # 🚨 الترقيع: تم إزالة _check_for_updates() من هنا لمنع تداخله مع شاشة البداية (Splash)

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(40)

        self.title_label = QLabel("IlmQuiz")
        self.title_label.setObjectName("welcome_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.subtitle_label = QLabel("تحدي المعرفة الإسلامية")
        self.subtitle_label.setObjectName("welcome_subtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setSpacing(20)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton("ابدأ التحدي")
        self.start_btn.setObjectName("start_button")
        self.start_btn.setFixedSize(250, 60)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start_clicked)

        self.exit_btn = QPushButton("خروج")
        self.exit_btn.setObjectName("exit_button")
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
        self.start_requested.emit()

    def _check_for_updates(self):
        # Check settings before starting the background updater
        auto_update = self.view_model.settings.data["settings"].get("auto_update_enabled", True)
        if not auto_update:
            return

        current_version = const.APP_VERSION
        
        self.checker = UpdateChecker(current_version=current_version)
        self.checker.update_available.connect(self._show_update_dialog)
        self.checker.start()

    def _show_update_dialog(self, version: str, notes: str, url: str, expected_hash: str = ""):
        dialog = UpdateDialog(
            new_version=version,
            release_notes=notes,
            download_url=url,
            tts_engine=self.view_model.tts,
            parent=self
        )
        dialog.exec()

    # ==========================================
    # 🚀 الترقيع: إدارة أحداث الظهور والاختفاء
    # ==========================================
    def showEvent(self, event):
        """Called automatically when the screen becomes visible to the user."""
        super().showEvent(event)
        # Check for updates ONLY when the user actually sees this screen
        if not self._has_checked_updates:
            self._check_for_updates()
            self._has_checked_updates = True

    def hideEvent(self, event):
        """Called automatically by PySide6 when the widget is hidden."""
        # Clean up the background thread to prevent "C++ object deleted" crashes
        if self.checker and self.checker.isRunning():
            self.checker.quit()
            self.checker.wait()
        super().hideEvent(event)
