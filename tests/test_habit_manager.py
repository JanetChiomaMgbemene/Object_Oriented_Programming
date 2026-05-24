import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.habit           import TIME_WINDOWS
from managers.storage_manager import StorageManager
from managers.habit_manager   import HabitManager

def make_manager(tmp_path: str) -> HabitManager:
    storage = StorageManager(os.path.join(tmp_path, "habits.json"))
    hm = HabitManager(storage)
    return hm


def add_sample(hm: HabitManager, name="Morning Run",
               htype="build", window_index=1,
               freq="daily", reward="Coffee") -> object:
    return hm.add_habit(name, htype, window_index, freq, reward, "UTC")


class TestHabitManagerAddAndRetrieve(unittest.TestCase):
    def setUp(self):
        self.tmp    = tempfile.mkdtemp()
        self.hm     = make_manager(self.tmp)

    def test_add_habit_returns_habit_object(self):
        habit = add_sample(self.hm)
        self.assertEqual(habit.habit_name, "Morning Run")

    def test_add_habit_assigns_correct_window(self):
        habit = add_sample(self.hm, window_index=1)
        label, start, end = TIME_WINDOWS[1]
        self.assertEqual(habit.preferred_window, label)
        self.assertEqual(habit.scheduled_start,  start)
        self.assertEqual(habit.scheduled_end,    end)

    def test_add_habit_auto_increments_id(self):
        h1 = add_sample(self.hm, name="Run")
        h2 = add_sample(self.hm, name="Read")
        self.assertEqual(h1.habit_id, 1)
        self.assertEqual(h2.habit_id, 2)

    def test_add_habit_stores_timezone(self):
        self.hm.add_habit("Run", "build", 1, "daily", "Coffee", "Africa/Lagos")
        habit = self.hm.get_habits()[0]
        self.assertEqual(habit.timezone, "Africa/Lagos")

    def test_get_habits_returns_all(self):
        add_sample(self.hm, name="Run")
        add_sample(self.hm, name="Read")
        self.assertEqual(len(self.hm.get_habits()), 2)

    def test_get_habits_empty_list(self):
        self.assertEqual(self.hm.get_habits(), [])

    def test_get_habit_by_id_found(self):
        habit = add_sample(self.hm)
        result = self.hm.get_habit_by_id(habit.habit_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.habit_name, "Morning Run")

    def test_get_habit_by_id_not_found(self):
        result = self.hm.get_habit_by_id(999)
        self.assertIsNone(result)

    def test_habit_persisted_after_add(self):
        add_sample(self.hm, name="Persist Me")
        hm2 = make_manager(self.tmp)
        hm2.load()
        self.assertEqual(len(hm2.get_habits()), 1)
        self.assertEqual(hm2.get_habits()[0].habit_name, "Persist Me")


class TestHabitManagerDelete(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm  = make_manager(self.tmp)

    def test_delete_existing_habit_returns_true(self):
        habit = add_sample(self.hm)
        result = self.hm.delete_habit(habit.habit_id)
        self.assertTrue(result)

    def test_delete_removes_from_list(self):
        habit = add_sample(self.hm)
        self.hm.delete_habit(habit.habit_id)
        self.assertEqual(len(self.hm.get_habits()), 0)

    def test_delete_nonexistent_returns_false(self):
        result = self.hm.delete_habit(999)
        self.assertFalse(result)

    def test_delete_only_removes_correct_habit(self):
        h1 = add_sample(self.hm, name="Run")
        h2 = add_sample(self.hm, name="Read")
        self.hm.delete_habit(h1.habit_id)
        remaining = self.hm.get_habits()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].habit_name, "Read")


class TestHabitManagerUpdate(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm  = make_manager(self.tmp)
        self.habit = add_sample(self.hm)

    def test_update_reward(self):
        self.hm.update_habit(self.habit.habit_id, reward="Tea 🍵")
        updated = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertEqual(updated.reward, "Tea 🍵")

    def test_update_habit_name(self):
        self.hm.update_habit(self.habit.habit_id, habit_name="Evening Walk")
        updated = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertEqual(updated.habit_name, "Evening Walk")

    def test_update_time_window_via_window_index(self):
        self.hm.update_habit(self.habit.habit_id, window_index=5)
        updated = self.hm.get_habit_by_id(self.habit.habit_id)
        label, start, end = TIME_WINDOWS[5]
        self.assertEqual(updated.preferred_window, label)
        self.assertEqual(updated.scheduled_start,  start)
        self.assertEqual(updated.scheduled_end,    end)

    def test_update_nonexistent_returns_false(self):
        result = self.hm.update_habit(999, reward="Ghost")
        self.assertFalse(result)


class TestHabitManagerStartAndComplete(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm  = make_manager(self.tmp)
        self.habit = add_sample(self.hm)

    def test_start_habit_returns_time_string(self):
        result = self.hm.start_habit(self.habit.habit_id)
        self.assertIsInstance(result, str)
        self.assertIn("M", result)   # "AM" or "PM" should be present

    def test_start_habit_records_on_habit_object(self):
        self.hm.start_habit(self.habit.habit_id)
        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertIsNotNone(habit.actual_start_time)

    def test_start_nonexistent_habit_returns_none(self):
        result = self.hm.start_habit(999)
        self.assertIsNone(result)

    def test_mark_complete_with_timer_sets_status(self):
        self.hm.start_habit(self.habit.habit_id)
        result = self.hm.mark_complete(self.habit.habit_id, notes="Great", use_timer=True)
        self.assertTrue(result)
        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertEqual(habit.status, "complete")

    def test_mark_complete_without_timer(self):
        result = self.hm.mark_complete(self.habit.habit_id, use_timer=False)
        self.assertTrue(result)
        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertEqual(habit.status, "complete")

    def test_mark_complete_adds_history_entry(self):
        self.hm.start_habit(self.habit.habit_id)
        self.hm.mark_complete(self.habit.habit_id, notes="Done!", use_timer=True)
        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertEqual(len(habit.completion_history), 1)
        self.assertTrue(habit.completion_history[0]["completed"])

    def test_mark_complete_nonexistent_returns_false(self):
        result = self.hm.mark_complete(999)
        self.assertFalse(result)


class TestHabitManagerStreaks(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm  = make_manager(self.tmp)
        self.habit = add_sample(self.hm)

    def test_streak_increments_on_each_completion(self):
        for _ in range(3):
            self.hm.start_habit(self.habit.habit_id)
            self.hm.mark_complete(self.habit.habit_id, use_timer=True)

        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertEqual(habit.current_streak, 3)

    def test_longest_streak_updated(self):
        for _ in range(4):
            self.hm.start_habit(self.habit.habit_id)
            self.hm.mark_complete(self.habit.habit_id, use_timer=True)

        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        self.assertGreaterEqual(habit.longest_streak, 4)

    def test_streak_breaks_on_missed_entry(self):
        habit = self.hm.get_habit_by_id(self.habit.habit_id)
        habit.completion_history = [
            {"date": "2025-11-01", "completed": True,  "actual_start": "06:00 AM",
             "actual_end": "06:30 AM", "duration_mins": 30,
             "proof": None, "notes": "", "timezone": "UTC"},
            {"date": "2025-11-02", "completed": True,  "actual_start": "06:00 AM",
             "actual_end": "06:30 AM", "duration_mins": 30,
             "proof": None, "notes": "", "timezone": "UTC"},
            {"date": "2025-11-03", "completed": False, "actual_start": None,
             "actual_end": None, "duration_mins": None,
             "proof": None, "notes": "", "timezone": "UTC"},
        ]
        self.hm._update_streak(habit)
        self.assertEqual(habit.current_streak, 0)


class TestHabitManagerReset(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm  = make_manager(self.tmp)

    def test_reset_sets_daily_habits_to_pending(self):
        habit = add_sample(self.hm, freq="daily")
        self.hm.start_habit(habit.habit_id)
        self.hm.mark_complete(habit.habit_id, use_timer=True)

        self.hm.reset_daily_statuses()

        habit = self.hm.get_habit_by_id(habit.habit_id)
        self.assertEqual(habit.status, "pending")
        self.assertIsNone(habit.actual_start_time)
        self.assertIsNone(habit.actual_end_time)

    def test_reset_does_not_affect_weekly_habits(self):
        habit = add_sample(self.hm, freq="weekly")
        self.hm.start_habit(habit.habit_id)
        self.hm.mark_complete(habit.habit_id, use_timer=True)

        self.hm.reset_daily_statuses()

        habit = self.hm.get_habit_by_id(habit.habit_id)
        self.assertEqual(habit.status, "complete")

if __name__ == "__main__":
    unittest.main()