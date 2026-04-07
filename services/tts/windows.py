import logging
from .base import BaseTTS

logger = logging.getLogger(__name__)

class WindowsTTS(BaseTTS):
    """ TTS implementation using UniversalSpeech (NVDA/JAWS/SAPI) for Windows. """

    def __init__(self):
        self.available = False
        self.speech = None
        self.engine_name = "Unknown"

        try:
            from UniversalSpeech import UniversalSpeech
            self.speech = UniversalSpeech()
            self.available = True
            
            try:
                self.engine_name = self.speech.engine_used
            except Exception as e:
                logger.debug(f"Could not fetch engine_used: {e}")
                self.engine_name = "UniversalSpeech (Unknown)"

            logger.info(f"UniversalSpeech initialized successfully. Active engine: {self.engine_name}")

        except Exception as e:
            logger.exception("Failed to initialize UniversalSpeech on Windows.")

    def speak(self, text: str, interrupt: bool = True):
        if not self.available:
            return

        try:
            self.speech.say(text, interrupt)
            logger.debug(f"Speaking text: {text}")
        except Exception:
            logger.exception("Error during speech output")

    def speak_char(self, char: str):
        if not self.available or not char:
            return

        try:
            if char == " ":
                self.speech.say("space")
            elif char == "\n":
                self.speech.say("new line")
            elif ord(char) > 127:
                self.speech.say(char)
            else:
                self.speech.say_a(char)
        except Exception:
            logger.warning("say_a failed, falling back to speak()")
            self.speak(char)

    def stop(self):
        if not self.available:
            return
        try:
            self.speech.stop()
        except Exception:
            logger.exception("Error stopping speech")
