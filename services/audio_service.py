import os
import logging
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

logger = logging.getLogger(__name__)

class AudioService:
    """
    Manages and plays short sound effects for the game using PySide6 QtMultimedia.
    Optimized for low latency UI sounds like correct/wrong answers and timer beeps.
    """
    
    def __init__(self, sounds_dir: str = "assets/sounds"):
        self.sounds_dir = sounds_dir
        self.sounds = {}
        self.muted = False
        self._init_effects()

    def _init_effects(self):
        # Define the expected sound files
        # You need to place these .wav files in the assets/sounds directory
        sound_files = {
            "correct": "correct.wav",
            "wrong": "wrong.wav",
            "beep": "beep.wav",
            "time_up": "time_up.wav"
        }

        for name, filename in sound_files.items():
            file_path = os.path.join(self.sounds_dir, filename)
            effect = QSoundEffect()
            
            # Check if file exists to avoid silent runtime errors
            if os.path.exists(file_path):
                effect.setSource(QUrl.fromLocalFile(file_path))
                # Set default volume (0.0 to 1.0)
                effect.setVolume(0.8)
                self.sounds[name] = effect
            else:
                logger.warning(f"Sound file not found: {file_path}")

    def play_sound(self, name: str):
        """Plays a loaded sound effect by its registered name."""
        if self.muted:
            return
            
        effect = self.sounds.get(name)
        if effect:
            # Stop if currently playing to allow rapid replays (e.g., fast timer beeps)
            if effect.isPlaying():
                effect.stop()
            effect.play()
        else:
            logger.debug(f"Attempted to play unknown or missing sound: {name}")

    def toggle_mute(self) -> bool:
        """Toggles the mute state and returns the new state."""
        self.muted = not self.muted
        return self.muted
        
    def set_volume(self, volume: float):
        """Sets the volume for all loaded sound effects (0.0 to 1.0)."""
        vol = max(0.0, min(1.0, volume))
        for effect in self.sounds.values():
            effect.setVolume(vol)
