import json
import os
import logging
from core.constants import SETTINGS_PATH

logger = logging.getLogger(__name__)

class SettingsManager:
    """
    Manages user preferences and game progress in an external JSON file.
    If the user deletes this file, all progress and settings are reset to default.
    """
    def __init__(self, filepath: str = SETTINGS_PATH):
        self.filepath = filepath
        self.data = {
            "settings": {
                "tts_enabled": True,
                "audio_volume": 0.8
            },
            "progress": {} 
        }
        self.load()

    def load(self):
        """Loads data from the JSON file or creates a default one if it doesn't exist."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    # Update default dict with loaded data
                    if "progress" in file_data:
                        self.data["progress"].update(file_data["progress"])
                    if "settings" in file_data:
                        self.data["settings"].update(file_data["settings"])
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save(self):
        """Saves current data to the JSON file."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get_unlocked_level(self, topic_id: int) -> int:
        """Returns the highest unlocked level for a specific topic (1=Easy, 2=Medium, 3=Hard)."""
        topic_str = str(topic_id)
        return self.data["progress"].get(topic_str, 1)

    def unlock_next_level(self, topic_id: int, completed_level: int) -> bool:
        """Unlocks the next level if applicable and saves the progress."""
        topic_str = str(topic_id)
        current_unlocked = self.get_unlocked_level(topic_id)
        
        next_level = completed_level + 1
        
        # Changed 3 to 4 to track full completion (level 4 means all 3 levels are done)
        if next_level > current_unlocked and next_level <= 4:
            self.data["progress"][topic_str] = next_level
            self.save()
            return True
            
        return False
