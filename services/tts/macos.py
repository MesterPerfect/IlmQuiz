import subprocess
import threading
import queue
import logging
from .base import BaseTTS

logger = logging.getLogger(__name__)

class MacOSTTS(BaseTTS):
    """
    macOS TTS combining direct appscript (if available), 
    osascript fallback for VoiceOver, and the native 'say' command.
    """
    def __init__(self):
        self.available = True
        self.speech_queue = queue.Queue()
        self.current_process = None
        
        # Determine the best VoiceOver communication method
        self.vo_appscript_app = None
        self.has_appscript = False
        self.backend_name = "unknown"
        
        try:
            import appscript
            self.vo_appscript_app = appscript.app("voiceover")
            self.has_appscript = True
            self.backend_name = "VoiceOver (appscript)"
            logger.info("macOS TTS: 'appscript' module loaded successfully.")
            
        except ImportError:
            self.backend_name = "VoiceOver (osascript) or Say"
            logger.debug("macOS TTS: 'appscript' module not found, will use osascript/say fallback.")
            
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    # FIXED: Changed interrupt default to True to match BaseTTS and cross-platform behavior
    def speak(self, text: str, interrupt: bool = True):
        if interrupt:
            self.stop()
            with self.speech_queue.mutex:
                self.speech_queue.queue.clear()
        self.speech_queue.put(text)

    def speak_char(self, char: str):
        if not char:
            return
        if char == " ":
            self.speak("space", interrupt=True)
        else:
            self.speak(char, interrupt=True)

    def stop(self):
        # 1. Stop direct appscript VoiceOver output
        if self.has_appscript and self.vo_appscript_app and self.vo_appscript_app.isrunning():
            try:
                self.vo_appscript_app.output("")
            except Exception:
                pass
                
        # 2. Terminate the active process (say or osascript) if running
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
            except Exception:
                pass

    def _is_voiceover_running_cmd(self) -> bool:
        """Check VoiceOver status via command line if appscript is missing."""
        try:
            output = subprocess.check_output(
                ['osascript', '-e', 'tell application "System Events" to (name of processes) contains "VoiceOver"'],
                text=True, stderr=subprocess.DEVNULL
            )
            return "true" in output.strip().lower()
        except Exception:
            return False

    def _process_queue(self):
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
                
            try:
                # Approach 1: Use direct appscript if available and VO is running
                if self.has_appscript and self.vo_appscript_app and self.vo_appscript_app.isrunning():
                    self.vo_appscript_app.output(text)
                    
                # Approach 2: Use osascript to tell VoiceOver to speak
                elif not self.has_appscript and self._is_voiceover_running_cmd():
                    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
                    script = f'tell application "VoiceOver" to output "{escaped_text}"'
                    
                    # FIXED: Use Popen instead of run() so it can be terminated by stop() if interrupted
                    self.current_process = subprocess.Popen(
                        ['osascript', '-e', script], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    self.current_process.wait()
                    
                # Approach 3: Fallback to native 'say' command
                else:
                    self.current_process = subprocess.Popen(['say', text])
                    self.current_process.wait()
                    
            except Exception as e:
                # General fallback to 'say' if osascript fails unexpectedly
                logger.debug(f"macOS TTS approach failed, falling back to 'say'. Error: {e}")
                self.current_process = subprocess.Popen(['say', text])
                self.current_process.wait()
            
            self.speech_queue.task_done()

    def shutdown(self):
        self.stop()
        self.speech_queue.put(None)
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
