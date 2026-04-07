import logging
from .base import BaseTTS

logger = logging.getLogger(__name__)

class DummyTTS(BaseTTS):
    """ Fallback TTS engine that silently logs output when no real engine is available. """
    
    def __init__(self):
        self.available = False
        self.engine_name = "DummyTTS"
        logger.info("Dummy TTS initialized (Audio output is disabled).")

    def speak(self, text: str, interrupt: bool = True):
        logger.debug(f"[DummyTTS] Speak: {text}")

    def speak_char(self, char: str):
        logger.debug(f"[DummyTTS] Speak char: {repr(char)}")

    def stop(self):
        logger.debug("[DummyTTS] Stop speech")
