import os
import tempfile
import urllib.request
import logging
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

class UpdateDownloader(QThread):
    """
    Asynchronously downloads the update file and reports progress.
    """
    progress_updated = Signal(int)
    download_complete = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, download_url: str, target_version: str):
        super().__init__()
        self.download_url = download_url
        self.target_version = target_version
        
        filename = download_url.split("/")[-1]
        self.download_path = os.path.join(tempfile.gettempdir(), f"ilmquiz_update_{filename}")
        self._is_cancelled = False

    def run(self):
        try:
            logger.info(f"Starting update download from: {self.download_url}")
            req = urllib.request.Request(self.download_url, headers={'User-Agent': 'IlmQuiz-App'})
            
            with urllib.request.urlopen(req, timeout=15) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                chunk_size = 8192
                
                with open(self.download_path, 'wb') as file:
                    while True:
                        if self._is_cancelled:
                            logger.info("Update download cancelled.")
                            return
                            
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                            
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
                            
            logger.info(f"Download complete: {self.download_path}")
            self.download_complete.emit(self.download_path)
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.error_occurred.emit("فشل تنزيل التحديث. يرجى المحاولة مرة أخرى لاحقاً.")
            
    def cancel(self):
        self._is_cancelled = True
