import sys
import os
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QProgressBar, QMessageBox,
    QApplication
)
from PySide6.QtCore import Qt

from services.updater import UpdateDownloader

logger = logging.getLogger(__name__)

class UpdateDialog(QDialog):
    """
    Dialog to notify the user of an update, display release notes,
    and handle the downloading process with a progress bar.
    """
    def __init__(self, new_version: str, release_notes: str, download_url: str, tts_engine, parent=None):
        super().__init__(parent)
        self.new_version = new_version
        self.release_notes = release_notes
        self.download_url = download_url
        self.tts = tts_engine
        
        self.downloader = None
        self.last_announced_progress = 0

        self._setup_ui()
        self._announce_update()

    def _setup_ui(self):
        self.setWindowTitle("تحديث جديد متاح")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel(f"<b>يتوفر إصدار جديد: v{self.new_version}</b>")
        self.title_label.setObjectName("welcome_subtitle") # Reusing style
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Release Notes Text Area (Read-only)
        self.notes_edit = QTextEdit()
        self.notes_edit.setReadOnly(True)
        self.notes_edit.setPlainText(self.release_notes)
        self.notes_edit.setAccessibleName("ملاحظات الإصدار") 
        layout.addWidget(self.notes_edit)

        # Progress Bar (Hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Buttons Layout
        self.buttons_layout = QHBoxLayout()
        
        # 1. زر نسخ المستجدات
        self.btn_copy = QPushButton("نسخ الملاحظات")
        self.btn_copy.setObjectName("action_button")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.clicked.connect(self._copy_release_notes)
        self.buttons_layout.addWidget(self.btn_copy)
        
        self.buttons_layout.addStretch()
        
        # 2. زر التحديث
        self.btn_update = QPushButton("تحديث الآن")
        self.btn_update.setObjectName("action_button")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self._start_download)
        self.buttons_layout.addWidget(self.btn_update)
        
        # 3. زر الإلغاء/التأجيل
        self.btn_later = QPushButton("لاحقاً")
        self.btn_later.setObjectName("action_button")
        self.btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_later.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.btn_later)
        
        layout.addLayout(self.buttons_layout)

    def _copy_release_notes(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.release_notes)
        if self.tts:
            self.tts.speak("تم نسخ ملاحظات الإصدار للحافظة.")
        logger.info("Release notes copied to clipboard.")

    def _announce_update(self):
        msg = f"تحديث متاح. الإصدار {self.new_version}. اضغط مفتاح التبويب لقراءة الملاحظات أو التحديث."
        if self.tts:
            self.tts.speak(msg)

    def _start_download(self):
        self.btn_update.hide()
        self.btn_copy.hide()
        self.btn_later.setText("إلغاء")
        self.btn_later.clicked.disconnect()
        self.btn_later.clicked.connect(self._cancel_download)
        self.progress_bar.show()
        
        if self.tts:
            self.tts.speak("جاري بدء التحميل. يرجى الانتظار.")

        self.downloader = UpdateDownloader(self.download_url, self.new_version)
        self.downloader.progress_updated.connect(self._on_progress_updated)
        self.downloader.download_complete.connect(self._on_download_complete)
        self.downloader.error_occurred.connect(self._on_download_error)
        self.downloader.start()

    def _on_progress_updated(self, value: int):
        self.progress_bar.setValue(value)
        if value - self.last_announced_progress >= 25:
            self.last_announced_progress = value
            if self.tts:
                self.tts.speak(f"{value} بالمائة")

    def _on_download_complete(self, file_path: str):
        if self.tts:
            self.tts.speak("اكتمل التحميل. سيتم إغلاق التطبيق لتثبيت التحديث.")
            
        logger.info(f"Update downloaded to: {file_path}")
        
        QMessageBox.information(
            self, "اكتمل التحميل", 
            "تم تنزيل التحديث بنجاح. سيتم الآن إغلاق اللعبة لتطبيق التحديث."
        )
        
        self._launch_update_file(file_path)
        self.accept()
        sys.exit(0)

    def _on_download_error(self, error_msg: str):
        if self.tts:
            self.tts.speak("فشل التحميل.")
            
        QMessageBox.critical(self, "خطأ في التحديث", error_msg)
        
        self.progress_bar.hide()
        self.btn_update.show()
        self.btn_copy.show()
        self.btn_later.setText("لاحقاً")
        self.btn_later.clicked.disconnect()
        self.btn_later.clicked.connect(self.reject)

    def _cancel_download(self):
        if self.downloader and self.downloader.isRunning():
            self.downloader.cancel()
            self.downloader.wait()
            
        if self.tts:
            self.tts.speak("تم إلغاء التحميل.")
        self.reject()

    def _launch_update_file(self, file_path: str):
        import subprocess
        
        # 1. Handle Inno Setup (.exe) for Windows Installed Mode
        if file_path.lower().endswith('.exe'):
            # Run the Inno Setup installer silently. 
            # It will auto-close the current app and restart it.
            args = [
                file_path,
                "/VERYSILENT",        # No UI at all
                "/SUPPRESSMSGBOXES",  # Auto-click "Yes" to any prompts
                "/CLOSEAPPLICATIONS", # Force close IlmQuiz.exe
                "/RESTARTAPPLICATIONS" # Restart after install
            ]
            subprocess.Popen(args)
            return

        # 2. Handle Zip/Tar Archives for Portable / Mac / Linux Mode
        if getattr(sys, 'frozen', False):
            target_dir = os.path.dirname(sys.executable)
            main_exe = os.path.basename(sys.executable)
            updater_exe = "apply_update.exe" if sys.platform == "win32" else "apply_update"
            updater_path = os.path.join(target_dir, updater_exe)
            
            if os.path.exists(updater_path):
                args = [
                    updater_path, 
                    "--archive", file_path, 
                    "--target", target_dir, 
                    "--exe", main_exe
                ]
                
                if sys.platform == "win32":
                    subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)
                else:
                    subprocess.Popen(args, start_new_session=True)
            else:
                logger.error("Updater executable not found. Unable to self-update.")
                QMessageBox.warning(self, "خطأ", "ملف المُحدّث التلقائي غير موجود.")
        else:
            QMessageBox.information(
                self, "وضع المطور", 
                f"تم التحميل إلى:\n{file_path}\n\nبما أنك في وضع المطور، لن يعمل المُحدّث التلقائي."
            )
            folder = os.path.dirname(file_path)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.call(["open", folder])
            else:
                subprocess.call(["xdg-open", folder])
