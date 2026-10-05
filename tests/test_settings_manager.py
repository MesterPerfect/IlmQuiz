import unittest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.settings_manager import SettingsManager

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.settings = SettingsManager(self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_default_settings(self):
        data = self.settings.data["settings"]
        self.assertTrue(data.get("tts_enabled"))
        self.assertEqual(data.get("question_time"), 30)

    def test_unlock_levels(self):
        self.assertEqual(self.settings.get_unlocked_level(10), 1)
        unlocked = self.settings.unlock_next_level(10, completed_level=1)
        self.assertTrue(unlocked)
        self.assertEqual(self.settings.get_unlocked_level(10), 2)

    def test_achievements(self):
        self.assertEqual(len(self.settings.get_achievements()), 0)
        unlocked = self.settings.unlock_achievement("first_win")
        self.assertTrue(unlocked)
        self.assertIn("first_win", self.settings.get_achievements())
        # Duplicate unlock should return False
        self.assertFalse(self.settings.unlock_achievement("first_win"))

    def test_export_import_backup(self):
        self.settings.unlock_achievement("perfect_score")
        self.settings.unlock_next_level(5, 1)

        backup_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        backup_file.close()

        export_ok = self.settings.export_data(backup_file.name)
        self.assertTrue(export_ok)

        # Create fresh settings manager
        new_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        new_temp.close()
        new_settings = SettingsManager(new_temp.name)

        import_ok = new_settings.import_data(backup_file.name)
        self.assertTrue(import_ok)
        self.assertEqual(new_settings.get_unlocked_level(5), 2)
        self.assertIn("perfect_score", new_settings.get_achievements())

        if os.path.exists(backup_file.name):
            os.remove(backup_file.name)
        if os.path.exists(new_temp.name):
            os.remove(new_temp.name)

    def test_user_data_path(self):
        import core.constants as const
        if not const.IS_PORTABLE:
            self.assertIn("tecwindow", const.USER_DATA_DIR)
            self.assertTrue(const.USER_DATA_DIR.endswith("IlmQuiz"))

if __name__ == "__main__":
    unittest.main()
