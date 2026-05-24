import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.reward_manager import RewardManager
from models.habit import Habit


def make_habit(reward=""):
    return Habit(
        habit_id=1, habit_name="Test", habit_type="build",
        preferred_window="Morning", scheduled_start="06:00",
        scheduled_end="09:00", frequency="daily",
        reward=reward, timezone="UTC",
    )

class TestAssignReward(unittest.TestCase):

    def setUp(self):
        self.rm = RewardManager()

    def test_returns_existing_reward_if_set(self):
        habit = make_habit(reward="Coffee ☕")
        result = self.rm.assign_reward(habit)
        self.assertEqual(result, "Coffee ☕")

    def test_does_not_change_reward_if_already_set(self):
        habit = make_habit(reward="Movie night 🎬")
        self.rm.assign_reward(habit)
        self.assertEqual(habit.reward, "Movie night 🎬")

    def test_picks_default_when_reward_is_empty(self):
        habit = make_habit(reward="")
        result = self.rm.assign_reward(habit)
        self.assertIn(result, RewardManager.DEFAULT_REWARDS)

    def test_sets_reward_on_habit_when_empty(self):
        habit = make_habit(reward="")
        result = self.rm.assign_reward(habit)
        self.assertEqual(habit.reward, result)

    def test_default_rewards_list_is_not_empty(self):
        self.assertGreater(len(RewardManager.DEFAULT_REWARDS), 0)

    def test_all_default_rewards_are_strings(self):
        for reward in RewardManager.DEFAULT_REWARDS:
            self.assertIsInstance(reward, str)
            self.assertGreater(len(reward), 0)


class TestVerifyProof(unittest.TestCase):

    def setUp(self):
        self.rm  = RewardManager()
        self.tmp = tempfile.mkdtemp()

    def _make_file(self, filename: str) -> str:
        path = os.path.join(self.tmp, filename)
        with open(path, "w") as f:
            f.write("")   
        return path


    def test_valid_jpg_file(self):
        path = self._make_file("proof.jpg")
        self.assertTrue(self.rm.verify_proof(path))

    def test_valid_jpeg_file(self):
        path = self._make_file("proof.jpeg")
        self.assertTrue(self.rm.verify_proof(path))

    def test_valid_png_file(self):
        path = self._make_file("proof.png")
        self.assertTrue(self.rm.verify_proof(path))

    def test_valid_gif_file(self):
        path = self._make_file("proof.gif")
        self.assertTrue(self.rm.verify_proof(path))

    def test_valid_bmp_file(self):
        path = self._make_file("proof.bmp")
        self.assertTrue(self.rm.verify_proof(path))

    def test_valid_webp_file(self):
        path = self._make_file("proof.webp")
        self.assertTrue(self.rm.verify_proof(path))

    def test_uppercase_extension_accepted(self):
        path = self._make_file("PROOF.JPG")
        self.assertTrue(self.rm.verify_proof(path))


    def test_nonexistent_file_returns_false(self):
        fake_path = os.path.join(self.tmp, "ghost.jpg")
        self.assertFalse(self.rm.verify_proof(fake_path))

    def test_text_file_returns_false(self):
        path = self._make_file("notes.txt")
        self.assertFalse(self.rm.verify_proof(path))

    def test_pdf_file_returns_false(self):
        path = self._make_file("report.pdf")
        self.assertFalse(self.rm.verify_proof(path))

    def test_empty_string_returns_false(self):
        self.assertFalse(self.rm.verify_proof(""))

    def test_none_returns_false(self):
        self.assertFalse(self.rm.verify_proof(None))

    def test_no_extension_file_returns_false(self):
        path = self._make_file("no_extension")
        self.assertFalse(self.rm.verify_proof(path))


if __name__ == "__main__":
    unittest.main()