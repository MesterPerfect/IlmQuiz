import logging

logger = logging.getLogger(__name__)

class BaseTTS:
    """ Base interface for all TTS engines. """

    def speak(self, text: str, interrupt: bool = True):
        raise NotImplementedError("speak method must be implemented by subclass")

    def speak_char(self, char: str):
        raise NotImplementedError("speak_char method must be implemented by subclass")

    def stop(self):
        pass
