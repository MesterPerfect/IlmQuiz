import json
import platform
import urllib.request
import logging
from core.constants import IS_PORTABLE
from packaging.version import parse as parse_version
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

UPDATE_JSON_URL = "https://raw.githubusercontent.com/MesterPerfect/IlmQuiz/master/update.json"

class UpdateChecker(QThread):
    """
    Asynchronously checks a remote JSON manifest for the latest application version.
    """
    update_available = Signal(str, str, str) # version, notes, download_url
    no_update = Signal()
    error_occurred = Signal(str)

    def __init__(self, current_version: str, current_language: str = "ar", update_channel: str = "stable"):
        super().__init__()
        self.current_version = current_version
        self.current_language = current_language
        self.update_channel = update_channel

    def run(self):
        try:
            logger.info(f"Checking for updates from: {UPDATE_JSON_URL} on channel: {self.update_channel}")
            
            import time
            # Prevent caching by appending a timestamp query parameter
            url_with_nocache = f"{UPDATE_JSON_URL}?t={int(time.time())}"
            req = urllib.request.Request(url_with_nocache, headers={'User-Agent': 'IlmQuiz-App'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                master_data = json.loads(response.read().decode())
            
            channel_data = master_data.get(self.update_channel)
            if not channel_data:
                logger.error(f"Channel '{self.update_channel}' not found.")
                self.error_occurred.emit(f"Update channel '{self.update_channel}' is not available.")
                return

            latest_version = channel_data.get("version", "")
            
            if self._is_newer(latest_version, self.current_version):
                notes_dict = channel_data.get("release_notes", {})
                # Fetch notes in the preferred language, fallback to English
                localized_notes = notes_dict.get(self.current_language, notes_dict.get("en", "Update available."))
                
                current_os = platform.system().lower() # 'windows', 'darwin', or 'linux'
                os_downloads = channel_data.get("downloads", {}).get(current_os, {})
                
                # Fetch the correct URL based on execution mode
                if IS_PORTABLE:
                    download_url = os_downloads.get("portable", "")
                else:
                    download_url = os_downloads.get("installed", "")
                    
                # Emit the signal if a valid URL is found
                if download_url:
                    self.update_available.emit(latest_version, localized_notes, download_url)
                else:
                    self.error_occurred.emit("لم يتم العثور على ملف تحديث مناسب لنظام التشغيل أو نوع النسخة الخاص بك.")
            else:
                self.no_update.emit()
                
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            self.error_occurred.emit("تعذر التحقق من التحديثات. يرجى التحقق من اتصالك بالإنترنت.")

    def _is_newer(self, latest: str, current: str) -> bool:
        try:
            return parse_version(latest) > parse_version(current)
        except Exception as e:
            logger.error(f"Version parsing error: {e}")
            return False
