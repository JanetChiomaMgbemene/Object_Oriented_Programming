import sys, os, unittest, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.habit import Habit
from managers.storage_manager import StorageManager

def mh(i, name="Test"):
    return Habit(i, name, "build", "Morning","06:00","09:00","daily","Coffee","UTC")

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.store = StorageManager(os.path.join(self.tmp, "habits.json"))

    def test_save_and_load(self):
        self.store.save_habits([mh(1)])
        loaded = self.store.load_habits()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].preferred_window, "Morning")

    def test_missing_file_returns_empty(self):
        self.assertEqual(self.store.load_habits(), [])

    def test_multiple_habits(self):
        self.store.save_habits([mh(i,f"H{i}") for i in range(1,4)])
        self.assertEqual(len(self.store.load_habits()), 3)

    def test_overwrite(self):
        h = mh(1); self.store.save_habits([h])
        h.reward = "Tea"; self.store.save_habits([h])
        self.assertEqual(self.store.load_habits()[0].reward, "Tea")

if __name__ == "__main__": unittest.main()