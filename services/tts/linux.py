import subprocess
import logging
import shutil
import threading
import queue
from typing import Callable, Dict, Optional, Tuple

from .base import BaseTTS

logger = logging.getLogger(__name__)

class LinuxTTS(BaseTTS):
    """
    Linux TTS with prioritized backends:
    1. Direct python-speechd library
    2. DBus (Orca v49+)
    3. Qt Accessibility
    4. SPD CLI fallback
    """

    def __init__(self):
        self.qt_module: Optional[str] = None
        self.QAccessible = None
        self.QAccessibleAnnouncementEvent = None
        self.QApplication = None

        self._speechd_client = None
        self._speechd_is_speaking = False

        self._backends: Dict[str, Callable] = {
            "python_speechd": self._speak_python_speechd,
            "dbus": self._speak_dbus,
            "qt": self._speak_qt,
            "spd": self._speak_spd,
        }

        self.backend = self._detect_backend()

        self._queue: queue.Queue[Tuple[str, bool]] = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

        logger.info(f"LinuxTTS initialized with backend: {self.backend}")

    def _detect_backend(self) -> str:
        if self._init_python_speechd():
            return "python_speechd"
        if self._has_dbus_orca():
            return "dbus"
        if self._has_qt_announcement():
            return "qt"
        return "spd"

    def _init_python_speechd(self) -> bool:
        try:
            import speechd
            self.speechd_module = speechd
            self._speechd_client = speechd.SSIPClient("ilmquiz")
            return True
        except ImportError:
            return False
        except Exception:
            return False

    def _has_dbus_orca(self) -> bool:
        import re
        if not shutil.which("gdbus"):
            return False
        try:
            out = subprocess.check_output(
                ["orca", "--version"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            match = re.search(r"(\d+)", out)
            if match and int(match.group(1)) >= 49:
                return True
        except Exception:
            return False
        return False

    def _has_qt_announcement(self) -> bool:
        try:
            from PySide6.QtGui import QAccessible, QAccessibleAnnouncementEvent
            from PySide6.QtWidgets import QApplication
            self.qt_module = "PySide6"
        except ImportError:
            return False

        self.QAccessible = QAccessible
        self.QAccessibleAnnouncementEvent = QAccessibleAnnouncementEvent
        self.QApplication = QApplication
        return True

    def speak(self, text: str, interrupt: bool = True):
        if not text: return

        if self.backend == "qt":
            if interrupt:
                self.stop()
            self._speak_qt(text, interrupt)
            return

        if interrupt:
            self._clear_queue()
            self.stop()

        self._queue.put((text, interrupt))

    def speak_char(self, char: str):
        if not char: return
        if char == " ":
            self.speak("space", interrupt=True)
        else:
            self.speak(char, interrupt=True)

    def stop(self):
        self._clear_queue()
        if self.backend == "python_speechd" and self._speechd_client:
            try:
                self._speechd_client.cancel()
            except Exception:
                pass
        elif self.backend == "spd":
            try:
                subprocess.Popen(["spd-say", "-C"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def shutdown(self):
        self._stop_event.set()
        self._queue.put(("__STOP__", True))
        self._worker_thread.join(timeout=1)
        if self._speechd_client:
            try:
                self._speechd_client.close()
            except Exception:
                pass

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                text, interrupt = self._queue.get()
                if text == "__STOP__": break
                backend_func = self._backends.get(self.backend)
                if backend_func:
                    backend_func(text, interrupt)
            except Exception as e:
                logger.error(f"TTS worker error: {e}")

    def _clear_queue(self):
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def _speechd_callback(self, callback_type):
        if callback_type == self.speechd_module.CallbackType.BEGIN:
            self._speechd_is_speaking = True
        elif callback_type in (self.speechd_module.CallbackType.END, self.speechd_module.CallbackType.CANCEL):
            self._speechd_is_speaking = False

    def _speak_python_speechd(self, text: str, interrupt: bool = True):
        if not self._speechd_client: return
        try:
            self._speechd_client.speak(
                text, 
                callback=self._speechd_callback,
                event_types=(
                    self.speechd_module.CallbackType.BEGIN,
                    self.speechd_module.CallbackType.CANCEL,
                    self.speechd_module.CallbackType.END
                )
            )
        except Exception:
            pass

    def _speak_dbus(self, text: str, interrupt: bool = True):
        try:
            safe_text = text.replace("'", "\\'")
            gvariant_str = f"'{safe_text}'"
            subprocess.Popen([
                "gdbus", "call", "--session", "--dest", "org.gnome.Orca",
                "--object-path", "/org/gnome/Orca", "--method", "org.gnome.Orca.PresentMessage",
                gvariant_str,
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def _speak_qt(self, text: str, interrupt: bool = True):
        try:
            politeness = (
                self.QAccessible.AnnouncementPoliteness.Assertive
                if interrupt else self.QAccessible.AnnouncementPoliteness.Polite
            )
            app = self.QApplication.instance()
            if not app: return
            widget = app.activeWindow() or app.focusWidget()
            if widget is None: return

            event = self.QAccessibleAnnouncementEvent(widget, text)
            event.setPoliteness(politeness)
            self.QAccessible.updateAccessibility(event)
        except Exception:
            pass

    def _speak_spd(self, text: str, interrupt: bool = True):
        try:
            subprocess.Popen(["spd-say", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
