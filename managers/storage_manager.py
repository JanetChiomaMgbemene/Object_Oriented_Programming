import json
import os        # built-in library for file and folder operations
from models.habit import Habit


class StorageManager:

    def __init__(self, file_path: str = "data/habits.json"):        # Sets up the StorageManager.
        self.file_path = file_path


    def save_habits(self, habit_list: list) -> None:
        folder = os.path.dirname(self.file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)   # creates the folder

        habits_as_dicts = [habit.to_dict() for habit in habit_list]
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(habits_as_dicts, file, indent=4)
           
    def load_habits(self) -> list:        # If the file doesn't exist, there's nothing to load — return empty list
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r", encoding="utf-8") as file:
            try:
                habits_as_dicts = json.load(file)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, return an empty list, instead of crashing
                print(f"Warning: Could not read {self.file_path}. Starting fresh.")
                return []

        # Convert each dict back into a Habit object using Habit.from_dict()
        habit_list = [Habit.from_dict(data) for data in habits_as_dicts]
        return habit_list