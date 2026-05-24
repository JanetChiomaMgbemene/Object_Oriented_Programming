import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.storage_manager    import StorageManager
from managers.habit_manager      import HabitManager
from managers.timetable_manager  import TimetableManager


def make_hm_and_tm(tmp_path: str):
    storage = StorageManager(os.path.join(tmp_path, "habits.json"))
    hm = HabitManager(storage)
    tm = TimetableManager(hm)
    return hm, tm


def add(hm, name, window_index=1, freq="daily"):
    return hm.add_habit(name, "build", window_index, freq, "Coffee", "UTC")


class TestTimetableOrganise(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm, self.tm = make_hm_and_tm(self.tmp)

    def test_empty_habits_gives_empty_structure(self):
        result = self.tm.get_timetable()
        self.assertEqual(result, [])

    def test_single_habit_produces_one_row(self):
        add(self.hm, "Run", window_index=1)
        result = self.tm.get_timetable()
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 1)

    def test_sorted_by_scheduled_start(self):
        add(self.hm, "Night Habit",   window_index=6)  
        add(self.hm, "Morning Habit", window_index=1)  
        result = self.tm.get_timetable()

        first_habit = result[0][0]
        self.assertEqual(first_habit.habit_name, "Morning Habit")

    def test_habits_in_same_window_are_grouped(self):
        add(self.hm, "Run",   window_index=1)   # Morning
        add(self.hm, "Water", window_index=1)   # Morning
        result = self.tm.get_timetable()
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)

    def test_habits_in_different_windows_are_separate_rows(self):
        add(self.hm, "Run",  window_index=1)   # Morning
        add(self.hm, "Read", window_index=6)   # Night
        result = self.tm.get_timetable()
        self.assertEqual(len(result), 2)

    def test_three_windows_sorted_correctly(self):
        add(self.hm, "Night Read",  window_index=6)  
        add(self.hm, "Afternoon",   window_index=3)   
        add(self.hm, "Morning Run", window_index=1)  
        result = self.tm.get_timetable()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0].habit_name, "Morning Run")
        self.assertEqual(result[1][0].habit_name, "Afternoon")
        self.assertEqual(result[2][0].habit_name, "Night Read")


class TestTimetableDisplay(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm, self.tm = make_hm_and_tm(self.tmp)

    def test_display_empty_shows_no_habits_message(self):
        output = self.tm.display_timetable()
        self.assertIn("No habits", output)

    def test_display_contains_habit_name(self):
        add(self.hm, "Morning Exercise", window_index=1)
        output = self.tm.display_timetable()
        self.assertIn("Morning Exercise", output)

    def test_display_contains_window_label(self):
        add(self.hm, "Run", window_index=1)  # Morning window
        output = self.tm.display_timetable()
        self.assertIn("Morning", output)

    def test_display_shows_pending_status(self):
        add(self.hm, "Run", window_index=1)
        output = self.tm.display_timetable()
        self.assertIn("pending", output)

    def test_display_shows_complete_status(self):
        habit = add(self.hm, "Run", window_index=1)
        self.hm.start_habit(habit.habit_id)
        self.hm.mark_complete(habit.habit_id, use_timer=True)
        output = self.tm.display_timetable()
        self.assertIn("complete", output)

    def test_display_shows_actual_start_time_when_started(self):
        habit = add(self.hm, "Run", window_index=1)
        self.hm.start_habit(habit.habit_id)
        output = self.tm.display_timetable()
        self.assertIn("Started", output)

    def test_display_shows_both_times_when_complete(self):
        habit = add(self.hm, "Run", window_index=1)
        self.hm.start_habit(habit.habit_id)
        self.hm.mark_complete(habit.habit_id, use_timer=True)
        output = self.tm.display_timetable()
        self.assertIn("↳", output)

    def test_display_returns_string(self):
        add(self.hm, "Run", window_index=1)
        output = self.tm.display_timetable()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)


class TestTimetableGetSlot(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hm, self.tm = make_hm_and_tm(self.tmp)

    def test_get_slot_returns_matching_habits(self):
        add(self.hm, "Morning Run",   window_index=1)   # Morning
        add(self.hm, "Morning Water", window_index=1)   # Morning
        add(self.hm, "Night Read",    window_index=6)   # Night
        result = self.tm.get_slot("Morning")
        self.assertEqual(len(result), 2)
        for h in result:
            self.assertEqual(h.preferred_window, "Morning")

    def test_get_slot_empty_for_unused_window(self):
        add(self.hm, "Run", window_index=1)   # Morning only
        result = self.tm.get_slot("Afternoon")
        self.assertEqual(result, [])

    def test_get_slot_empty_when_no_habits(self):
        result = self.tm.get_slot("Morning")
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()