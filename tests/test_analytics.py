import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, timedelta
from models.habit import Habit
from analytics.analytics import (calc_streak, completion_rate, filter_by_type,
    filter_by_window, weakest_habits, streak_at_risk, generate_report, avg_duration)

def mh(i, name, htype="build", window="Morning"):
    return Habit(i, name, htype, window, "06:00","09:00","daily","R","UTC")

def add(habit, n, miss_today=False):
    today = date.today()
    for i in range(n, 0, -1):
        d = (today - timedelta(days=i-1)).isoformat()
        done = not (miss_today and i == 1)
        habit.completion_history.append({
            "date": d, "completed": done,
            "actual_start": "06:30 AM", "actual_end": "07:00 AM",
            "duration_mins": 30 if done else None,
            "proof": None, "notes": "", "timezone": "UTC"
        })

class TestAnalytics(unittest.TestCase):
    def test_streak_all_complete(self):
        h = mh(1,"R"); add(h, 7)
        c, l = calc_streak(h)
        self.assertEqual(c, 7); self.assertEqual(l, 7)

    def test_streak_miss_today(self):
        h = mh(1,"R"); add(h, 7, miss_today=True)
        self.assertEqual(calc_streak(h)[0], 0)

    def test_rate_perfect(self):
        h = mh(1,"R"); add(h, 7)
        self.assertEqual(completion_rate(h, 7), 1.0)

    def test_rate_zero(self):
        self.assertEqual(completion_rate(mh(1,"R")), 0.0)

    def test_filter_by_type(self):
        hs = [mh(1,"A","build"), mh(2,"B","break"), mh(3,"C","build")]
        self.assertEqual(len(filter_by_type(hs,"build")), 2)

    def test_filter_by_window(self):
        hs = [mh(1,"A",window="Morning"), mh(2,"B",window="Night")]
        result = filter_by_window(hs, "Morning")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].habit_name, "A")

    def test_weakest(self):
        s = mh(1,"Strong"); add(s, 7)
        w = mh(2,"Weak")
        self.assertEqual(weakest_habits([s, w], 1)[0].habit_name, "Weak")

    def test_streak_at_risk(self):
        h = mh(1,"R"); add(h, 5, miss_today=True); h.current_streak = 4
        self.assertIn(h, streak_at_risk([h]))

    def test_avg_duration(self):
        h = mh(1,"R"); add(h, 3)
        self.assertEqual(avg_duration(h), 30.0)

    def test_generate_report(self):
        b = mh(1,"Run","build"); add(b, 7)
        k = mh(2,"NoJunk","break"); add(k, 4)
        r = generate_report([b, k])
        self.assertEqual(r["total_habits"], 2)
        self.assertEqual(r["build_habits"], 1)
        self.assertEqual(r["avg_duration_mins"], 30.0)

    def test_get_all_habits_returns_all(self):
        from analytics.analytics import get_all_habits
        h1, h2, h3 = mh(1,"A"), mh(2,"B"), mh(3,"C")
        result = get_all_habits([h1, h2, h3])
        self.assertEqual(len(result), 3)

    def test_get_all_habits_empty(self):
        from analytics.analytics import get_all_habits
        self.assertEqual(get_all_habits([]), [])

    def test_get_all_habits_returns_copy(self):
        from analytics.analytics import get_all_habits
        original = [mh(1,"A"), mh(2,"B")]
        result = get_all_habits(original)
        result.clear()
        self.assertEqual(len(original), 2)

    def test_get_habits_by_periodicity_daily(self):
        from analytics.analytics import get_habits_by_periodicity
        daily  = mh(1,"Daily",   htype="build"); daily.frequency  = "daily"
        weekly = mh(2,"Weekly",  htype="build"); weekly.frequency = "weekly"
        result = get_habits_by_periodicity([daily, weekly], "daily")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].habit_name, "Daily")

    def test_get_habits_by_periodicity_weekly(self):
        from analytics.analytics import get_habits_by_periodicity
        h1 = mh(1,"D"); h1.frequency = "daily"
        h2 = mh(2,"W"); h2.frequency = "weekly"
        h3 = mh(3,"W2"); h3.frequency = "weekly"
        result = get_habits_by_periodicity([h1, h2, h3], "weekly")
        self.assertEqual(len(result), 2)

    def test_get_habits_by_periodicity_none_matching(self):
        from analytics.analytics import get_habits_by_periodicity
        h = mh(1,"A"); h.frequency = "daily"
        result = get_habits_by_periodicity([h], "monthly")
        self.assertEqual(result, [])

    def test_longest_streak_all_finds_best(self):
        from analytics.analytics import longest_streak_all
        h1 = mh(1,"Low");  h1.longest_streak = 3
        h2 = mh(2,"High"); h2.longest_streak = 21
        h3 = mh(3,"Mid");  h3.longest_streak = 7
        name, streak = longest_streak_all([h1, h2, h3])
        self.assertEqual(name, "High")
        self.assertEqual(streak, 21)

    def test_longest_streak_all_empty(self):
        from analytics.analytics import longest_streak_all
        name, streak = longest_streak_all([])
        self.assertEqual(streak, 0)

    def test_longest_streak_for_habit_no_history(self):
        from analytics.analytics import longest_streak_for_habit
        h = mh(1,"Empty")
        self.assertEqual(longest_streak_for_habit(h), 0)

    def test_longest_streak_for_habit_with_completions(self):
        from analytics.analytics import longest_streak_for_habit
        h = mh(1,"Run"); add(h, 7)   # 7 consecutive completions
        result = longest_streak_for_habit(h)
        self.assertEqual(result, 7)

    def test_longest_streak_for_habit_with_gap(self):
        from analytics.analytics import longest_streak_for_habit
        h = mh(1,"Run")
        add(h, 3)
        h.completion_history.append({
            "date": "2025-01-01", "completed": False,
            "actual_start": None, "actual_end": None,
            "duration_mins": None, "proof": None, "notes": "", "timezone": "UTC"
        })
        add(h, 5)
        result = longest_streak_for_habit(h)
        self.assertEqual(result, 5)

if __name__ == "__main__": unittest.main()