import platform
import logging
from .dummy import DummyTTS

logger = logging.getLogger(__name__)

def create_tts(disable_tts: bool = False):
    """ Factory function to create the appropriate TTS engine based on OS. """
    if disable_tts:
        logger.info("TTS explicitly disabled.")
        return DummyTTS()
        
    system = platform.system()
    logger.info(f"Detected platform for TTS: {system}")

    try:
        if system == "Windows":
            from .windows import WindowsTTS
            tts = WindowsTTS()
            if getattr(tts, 'available', True):
                return tts
            logger.warning("UniversalSpeech unavailable, falling back to Dummy.")
            return DummyTTS()

        elif system == "Linux":
            from .linux import LinuxTTS
            return LinuxTTS()

        elif system == "Darwin":
            from .macos import MacOSTTS
            return MacOSTTS()

        else:
            logger.warning(f"Unsupported platform: {system}")
            return DummyTTS()
            
    except Exception as e:
        logger.error(f"Failed to initialize TTS engine for {system}: {e}")
        return DummyTTS()
