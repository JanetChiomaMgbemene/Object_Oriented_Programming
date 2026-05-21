import sys, os, unittest, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.habit import Habit, TIME_WINDOWS

def make_habit():
    return Habit(1,"Morning Run","build","Morning","06:00","09:00","daily","Coffee","UTC")

class TestHabit(unittest.TestCase):
    def test_attributes(self):
        h = make_habit()
        self.assertEqual(h.habit_id, 1)
        self.assertEqual(h.status, "pending")
        self.assertEqual(h.current_streak, 0)

    def test_start_records_time(self):
        h = make_habit()
        t = h.start_habit()
        self.assertIsInstance(t, str)
        self.assertEqual(h.actual_start_time, t)

    def test_mark_complete(self):
        h = make_habit()
        h.start_habit()
        e = h.mark_complete(notes="great")
        self.assertEqual(h.status, "complete")
        self.assertTrue(e["completed"])
        self.assertGreaterEqual(e["duration_mins"], 0)

    def test_mark_complete_without_timer(self):
        h = make_habit()
        e = h.mark_complete_without_timer()
        self.assertEqual(h.status, "complete")
        self.assertIsNone(e["actual_start"])
        self.assertIsNone(e["duration_mins"])

    def test_upload_proof(self):
        h = make_habit()
        h.start_habit(); h.mark_complete()
        h.upload_proof("uploads/run.jpg")
        self.assertEqual(h.proof_image_path, "uploads/run.jpg")
        self.assertEqual(h.completion_history[-1]["proof"], "uploads/run.jpg")

    def test_update_habit(self):
        h = make_habit()
        h.update_habit(reward="Tea", frequency="weekly")
        self.assertEqual(h.reward, "Tea")
        self.assertEqual(h.frequency, "weekly")

    def test_to_dict_has_window_fields(self):
        d = make_habit().to_dict()
        for key in ("preferred_window","scheduled_start","actual_start_time"):
            self.assertIn(key, d)

    def test_roundtrip(self):
        h = make_habit()
        loaded = Habit.from_dict(h.to_dict())
        self.assertEqual(loaded.habit_id, h.habit_id)
        self.assertEqual(loaded.timezone, h.timezone)
        self.assertEqual(loaded.preferred_window, h.preferred_window)

    def test_time_windows_valid(self):
        self.assertGreater(len(TIME_WINDOWS), 0)
        for lbl, s, e in TIME_WINDOWS:
            self.assertIn(":", s)
            self.assertIn(":", e)

if __name__ == "__main__": unittest.main()