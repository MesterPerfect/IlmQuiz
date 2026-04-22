import os
import tempfile
import urllib.request
import logging
import hashlib
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

class UpdateDownloader(QThread):
    """
    Asynchronously downloads the update file, verifies integrity, and reports progress.
    """
    progress_updated = Signal(int)
    download_complete = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, download_url: str, target_version: str, expected_hash: str = None):
        super().__init__()
        self.download_url = download_url
        self.target_version = target_version
        self.expected_hash = expected_hash  # Security: Expected SHA-256 hash
        
        filename = download_url.split("/")[-1]
        # Store in temp directory to avoid permission issues
        self.download_path = os.path.join(tempfile.gettempdir(), f"ilmquiz_update_{filename}")
        self._is_cancelled = False

    def run(self):
        try:
            logger.info(f"Starting update download from: {self.download_url}")
            req = urllib.request.Request(self.download_url, headers={'User-Agent': 'IlmQuiz-App'})
            
            # Initialize the SHA-256 hash object
            sha256_hash = hashlib.sha256()
            
            with urllib.request.urlopen(req, timeout=15) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                chunk_size = 8192
                
                with open(self.download_path, 'wb') as file:
                    while True:
                        if self._is_cancelled:
                            logger.info("Update download cancelled.")
                            file.close()
                            # Clean up the partial file if cancelled
                            if os.path.exists(self.download_path):
                                os.remove(self.download_path)
                            return
                            
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                            
                        file.write(chunk)
                        sha256_hash.update(chunk)  # Compute hash on the fly
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)

            # ==========================================
            # 🛡️ Security Check: Hash Verification
            # ==========================================
            if self.expected_hash:
                actual_hash = sha256_hash.hexdigest()
                if actual_hash.lower() != self.expected_hash.lower():
                    logger.error(f"Security Alert: Hash mismatch! Expected {self.expected_hash}, got {actual_hash}")
                    # Immediately delete the compromised or corrupted file
                    if os.path.exists(self.download_path):
                        os.remove(self.download_path)
                    
                    self.error_occurred.emit("تنبيه أمني: فشل التحقق من صحة ملف التحديث! تم إيقاف العملية لحمايتك.")
                    return
                    
            logger.info(f"Download and verification complete: {self.download_path}")
            self.download_complete.emit(self.download_path)
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.error_occurred.emit("فشل تنزيل التحديث. يرجى المحاولة مرة أخرى لاحقاً.")
            
    def cancel(self):
        self._is_cancelled = True
