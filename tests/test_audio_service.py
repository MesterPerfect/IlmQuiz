import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.audio_service import AudioService


class TestAudioService(unittest.TestCase):
    def setUp(self):
        self.audio = AudioService()

    def tearDown(self):
        self.audio.cleanup()

    def test_initialization(self):
        self.assertTrue(self.audio.available)
        self.assertIn("correct", self.audio.samples)
        self.assertIn("wrong", self.audio.samples)
        self.assertIn("beep", self.audio.samples)
        self.assertIn("time_up", self.audio.samples)

    def test_volume_controls(self):
        self.audio.set_volume(0.5)
        self.assertAlmostEqual(self.audio.get_volume(), 0.5)

        # Test percentage scale (50 -> 0.5)
        self.audio.set_volume(70)
        self.assertAlmostEqual(self.audio.get_volume(), 0.7)

        # Clamping
        self.audio.set_volume(-1.0)
        self.assertEqual(self.audio.get_volume(), 0.0)

    def test_toggle_mute(self):
        self.assertFalse(self.audio.muted)
        state = self.audio.toggle_mute()
        self.assertTrue(state)
        self.assertTrue(self.audio.muted)
        state = self.audio.toggle_mute()
        self.assertFalse(state)
        self.assertFalse(self.audio.muted)

    def test_play_and_stop(self):
        # Should not raise exception
        self.audio.play_sound("beep")
        self.audio.stop_sound("beep")
        self.audio.stop_all()


if __name__ == "__main__":
    unittest.main()
