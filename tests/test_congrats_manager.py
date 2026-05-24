import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.congrats_manager import CongratManager
from models.habit import Habit


def make_habit(streak=0, custom_message=""):
    h = Habit(
        habit_id=1, habit_name="Morning Run", habit_type="build",
        preferred_window="Morning", scheduled_start="06:00",
        scheduled_end="09:00", frequency="daily",
        reward="Coffee", timezone="UTC",
        custom_message=custom_message,
    )
    h.current_streak = streak
    return h


class TestMessagesListIntegrity(unittest.TestCase):

    def setUp(self):
        self.cm = CongratManager()

    def test_messages_list_not_empty(self):
        self.assertGreater(len(CongratManager.MESSAGES), 0)

    def test_all_messages_are_non_empty_strings(self):
        for msg in CongratManager.MESSAGES:
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0)


class TestGenerateMessage(unittest.TestCase):

    def setUp(self):
        self.cm = CongratManager()

    def test_returns_a_string(self):
        habit  = make_habit(streak=3)
        result = self.cm.generate_message(habit)
        self.assertIsInstance(result, str)

    def test_contains_habit_name(self):
        habit  = make_habit(streak=1)
        result = self.cm.generate_message(habit)
        self.assertIn("Morning Run", result)

    def test_includes_streak_when_greater_than_one(self):
        habit  = make_habit(streak=5)
        result = self.cm.generate_message(habit)
        self.assertIn("5", result)
        self.assertIn("streak", result)

    def test_no_streak_note_when_streak_is_one(self):
        habit  = make_habit(streak=1)
        result = self.cm.generate_message(habit)
        self.assertNotIn("1-day streak", result)

    def test_no_streak_note_when_streak_is_zero(self):
        habit  = make_habit(streak=0)
        result = self.cm.generate_message(habit)
        self.assertNotIn("streak", result.split("'Morning Run'")[1].split("\n")[0])

    def test_message_ends_with_content_from_messages_list(self):
        result = self.cm.generate_message(Habit)
        second_line = result.split("\n")[-1]
        self.assertIn(second_line, CongratManager.MESSAGES)


class TestGetRandomMessage(unittest.TestCase):

    def setUp(self):
        self.cm = CongratManager()

    def test_returns_a_string(self):
        result = self.cm.get_random_message()
        self.assertIsInstance(result, str)

    def test_result_is_from_messages_list(self):
        result = self.cm.get_random_message()
        self.assertIn(result, CongratManager.MESSAGES)

    def test_returns_different_messages_over_many_calls(self):
        results = {self.cm.get_random_message() for _ in range(50)}
        self.assertGreater(len(results), 1)


class TestGetCustomMessage(unittest.TestCase):

    def setUp(self):
        self.cm = CongratManager()

    def test_returns_custom_message_when_set(self):
        habit  = make_habit(custom_message="You are amazing, Janet! 🌟")
        result = self.cm.get_custom_message(habit)
        self.assertEqual(result, "You are amazing, Janet! 🌟")

    def test_does_not_call_generate_when_custom_set(self):
        habit  = make_habit(streak=10, custom_message="My personal message")
        result = self.cm.get_custom_message(habit)
        self.assertEqual(result, "My personal message")

    def test_falls_back_to_generate_when_no_custom(self):
        habit  = make_habit(streak=3, custom_message="")
        result = self.cm.get_custom_message(habit)
        self.assertIn("Morning Run", result)

    def test_falls_back_to_generate_when_custom_is_whitespace(self):
        habit  = make_habit(custom_message="   ")
        result = self.cm.get_custom_message(habit)
        self.assertEqual(result, "   ")


if __name__ == "__main__":
    unittest.main()