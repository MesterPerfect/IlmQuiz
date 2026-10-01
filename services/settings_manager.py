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
        
        # Added UI and Game defaults to ensure the app initializes correctly for new users
        self.data = {
            "settings": {
                "tts_enabled": True,
                "audio_volume": 0.8,
                "logging_enabled": True,
                "auto_update_enabled": True,
                "theme": "dark_theme",
                "font_scale": 100,
                "question_time": 30
            },
            "progress": {},
            "achievements": []
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
                    if "achievements" in file_data:
                        self.data["achievements"] = list(set(self.data.get("achievements", []) + file_data["achievements"]))
            except Exception as e:
                # Replaced print with proper logging
                logger.error(f"Failed to load settings from {self.filepath}: {e}")

    def save(self):
        """Saves current data to the JSON file."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            # Replaced print with proper logging
            logger.error(f"Failed to save settings to {self.filepath}: {e}")

    def export_data(self, target_filepath: str) -> bool:
        """Exports the full progress and settings to a user-chosen backup file."""
        try:
            with open(target_filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            logger.info(f"User progress exported successfully to {target_filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export data to {target_filepath}: {e}")
            return False

    def import_data(self, source_filepath: str) -> bool:
        """Imports settings and progress from a backup file."""
        if not os.path.exists(source_filepath):
            return False
        try:
            with open(source_filepath, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
            
            if "progress" in imported_data:
                self.data["progress"] = imported_data["progress"]
            if "settings" in imported_data:
                self.data["settings"] = imported_data["settings"]
            if "achievements" in imported_data:
                self.data["achievements"] = imported_data["achievements"]
                
            self.save()
            logger.info(f"User progress imported successfully from {source_filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import data from {source_filepath}: {e}")
            return False

    def get_achievements(self) -> list:
        """Returns list of unlocked achievement IDs."""
        return self.data.get("achievements", [])

    def unlock_achievement(self, badge_id: str) -> bool:
        """Unlocks an achievement badge if not already unlocked."""
        if "achievements" not in self.data:
            self.data["achievements"] = []
        if badge_id not in self.data["achievements"]:
            self.data["achievements"].append(badge_id)
            self.save()
            return True
        return False

    def get_unlocked_level(self, topic_id: int) -> int:
        """Returns the highest unlocked level for a specific topic (1=Easy, 2=Medium, 3=Hard)."""
        topic_str = str(topic_id)
        return self.data["progress"].get(topic_str, 1)

    def unlock_next_level(self, topic_id: int, completed_level: int) -> bool:
        """Unlocks the next level if applicable and saves the progress."""
        topic_str = str(topic_id)
        current_unlocked = self.get_unlocked_level(topic_id)
        
        next_level = completed_level + 1
        
        # 4 means all 3 levels are completed
        if next_level > current_unlocked and next_level <= 4:
            self.data["progress"][topic_str] = next_level
            self.save()
            return True
            
        return False

    def get_unlocked_random_stage(self) -> int:
        """Returns the highest unlocked stage in the Random Journey mode (Max 100)."""
        return self.data["progress"].get("random_stage", 1)

    def unlock_next_random_stage(self, completed_stage: int) -> bool:
        """Unlocks the next random stage up to 100."""
        current_unlocked = self.get_unlocked_random_stage()
        next_stage = completed_stage + 1
        
        if next_stage > current_unlocked and next_stage <= 100:
            self.data["progress"]["random_stage"] = next_stage
            self.save()
            return True
            
        return False
