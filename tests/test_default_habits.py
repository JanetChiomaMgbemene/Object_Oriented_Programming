import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.default_habits import DefaultHabitManager


class TestGetSuggestions(unittest.TestCase):

    def setUp(self):
        self.dhm = DefaultHabitManager()

    def test_returns_non_empty_list(self):
        result = self.dhm.get_suggestions()
        self.assertGreater(len(result), 0)

    def test_each_item_is_five_element_tuple(self):
        for item in self.dhm.get_suggestions():
            self.assertEqual(len(item), 5,
                             msg=f"Expected 5 elements in tuple, got: {item}")

    def test_filter_by_daily(self):
        result = self.dhm.get_suggestions(frequency="daily")
        self.assertGreater(len(result), 0)
        for name, htype, window, freq, reward in result:
            self.assertEqual(freq, "daily")

    def test_filter_by_weekly(self):
        result = self.dhm.get_suggestions(frequency="weekly")
        self.assertGreater(len(result), 0)
        for name, htype, window, freq, reward in result:
            self.assertEqual(freq, "weekly")

    def test_filter_by_monthly(self):
        result = self.dhm.get_suggestions(frequency="monthly")
        self.assertGreater(len(result), 0)
        for name, htype, window, freq, reward in result:
            self.assertEqual(freq, "monthly")

    def test_no_filter_returns_all_frequencies(self):
        all_results = self.dhm.get_suggestions()
        daily   = self.dhm.get_suggestions("daily")
        weekly  = self.dhm.get_suggestions("weekly")
        monthly = self.dhm.get_suggestions("monthly")
        self.assertEqual(len(all_results), len(daily) + len(weekly) + len(monthly))

    def test_invalid_frequency_returns_all(self):
        result = self.dhm.get_suggestions(frequency="hourly")
        all_results = self.dhm.get_suggestions()
        self.assertEqual(len(result), len(all_results))

    def test_habit_types_are_valid(self):
        for name, htype, window, freq, reward in self.dhm.get_suggestions():
            self.assertIn(htype, ("build", "break"),
                          msg=f"Invalid type '{htype}' for '{name}'")

    def test_windows_are_non_empty_strings(self):
        for name, htype, window, freq, reward in self.dhm.get_suggestions():
            self.assertIsInstance(window, str)
            self.assertGreater(len(window), 0)


class TestGetFourWeekSeed(unittest.TestCase):

    def setUp(self):
        self.dhm  = DefaultHabitManager()
        self.seed = self.dhm.get_four_week_seed(timezone="UTC")

    def test_returns_five_habits(self):
        self.assertEqual(len(self.seed), 5)

    def test_each_habit_has_unique_id(self):
        ids = [h.habit_id for h in self.seed]
        self.assertEqual(len(ids), len(set(ids)))

    def test_daily_habits_have_28_history_entries(self):
        daily_habits = [h for h in self.seed if h.frequency == "daily"]
        for habit in daily_habits:
            self.assertEqual(len(habit.completion_history), 28,
                             msg=f"{habit.habit_name} should have 28 entries")

    def test_weekly_habit_has_four_monday_entries(self):
        weekly = [h for h in self.seed if h.frequency == "weekly"]
        self.assertGreater(len(weekly), 0)
        for habit in weekly:
            # 4 weeks = exactly 4 Mondays
            self.assertEqual(len(habit.completion_history), 4,
                             msg=f"{habit.habit_name} should have 4 entries")

    def test_build_habits_have_actual_start_times_on_completions(self):
        build_habits = [h for h in self.seed if h.habit_type == "build"]
        for habit in build_habits:
            completed_entries = [e for e in habit.completion_history
                                 if e["completed"]]
            for entry in completed_entries:
                self.assertIsNotNone(entry["actual_start"],
                    msg=f"{habit.habit_name}: completed entry missing actual_start")

    def test_break_habits_have_no_actual_start(self):
        break_habits = [h for h in self.seed if h.habit_type == "break"]
        for habit in break_habits:
            for entry in habit.completion_history:
                if entry["completed"]:
                    self.assertIsNone(entry["actual_start"],
                        msg=f"{habit.habit_name}: break habit should have no start time")

    def test_completed_entries_have_actual_end_time(self):
        for habit in self.seed:
            for entry in habit.completion_history:
                if entry["completed"]:
                    self.assertIsNotNone(entry["actual_end"],
                        msg=f"{habit.habit_name}: completed entry missing actual_end")

    def test_habits_have_positive_streaks(self):
        for habit in self.seed:
            self.assertGreaterEqual(habit.current_streak, 0)

    def test_timezone_is_embedded(self):
        seed = self.dhm.get_four_week_seed(timezone="Africa/Lagos")
        for habit in seed:
            self.assertEqual(habit.timezone, "Africa/Lagos")
            for entry in habit.completion_history:
                self.assertEqual(entry["timezone"], "Africa/Lagos")

    def test_missed_days_are_marked_not_completed(self):
        exercise = next(h for h in self.seed if h.habit_id == 1)
        missed = [e for e in exercise.completion_history if not e["completed"]]
        self.assertGreater(len(missed), 0)


class TestSimulateTimes(unittest.TestCase):
    def setUp(self):
        self.dhm = DefaultHabitManager()

    def test_break_habit_returns_none_start(self):
        start, end, duration = self.dhm._simulate_times("00:00", "23:59", "break")
        self.assertIsNone(start)
        self.assertIsNone(duration)
        self.assertIsNotNone(end)

    def test_build_habit_returns_three_values(self):
        start, end, duration = self.dhm._simulate_times("06:00", "09:00", "build")
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)
        self.assertIsNotNone(duration)

    def test_duration_is_positive(self):
        _, _, duration = self.dhm._simulate_times("06:00", "09:00", "build")
        self.assertGreater(duration, 0)

    def test_returned_strings_contain_am_or_pm(self):
        start, end, _ = self.dhm._simulate_times("06:00", "09:00", "build")
        self.assertTrue(start.endswith("AM") or start.endswith("PM"),
                        msg=f"start time '{start}' should end with AM or PM")
        self.assertTrue(end.endswith("AM") or end.endswith("PM"),
                        msg=f"end time '{end}' should end with AM or PM")


if __name__ == "__main__":
    unittest.main()