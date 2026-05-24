from models.habit import Habit, TIME_WINDOWS
from managers.storage_manager import StorageManager


class HabitManager:
    def __init__(self, storage: StorageManager):
        self._storage = storage
        self.habit_list: list = []
        self._next_id: int = 1

    def load(self) -> None:
        self.habit_list = self._storage.load_habits()
        if self.habit_list:
            self._next_id = max(h.habit_id for h in self.habit_list) + 1

    def add_habit(
        self,
        habit_name: str,
        habit_type: str,
        window_index: int,      
        frequency: str,
        reward: str,
        timezone: str = "UTC",
        custom_message: str = "",
    ) -> Habit:
        label, sched_start, sched_end = TIME_WINDOWS[window_index]

        new_habit = Habit(
            habit_id         = self._next_id,
            habit_name       = habit_name,
            habit_type       = habit_type,
            preferred_window = label,
            scheduled_start  = sched_start,
            scheduled_end    = sched_end,
            frequency        = frequency,
            reward           = reward,
            timezone         = timezone,
            custom_message   = custom_message,
        )

        self.habit_list.append(new_habit)
        self._next_id += 1
        self._persist()
        return new_habit

    def start_habit(self, habit_id: int) -> str | None:
        habit = self.get_habit_by_id(habit_id)
        if habit is None:
            return None

        recorded_time = habit.start_habit() 
        self._persist()
        return recorded_time
    
    def mark_complete(
        self,
        habit_id: int,
        notes: str = "",
        use_timer: bool = True,
    ) -> bool:
        habit = self.get_habit_by_id(habit_id)
        if habit is None:
            return False

        if use_timer:
            habit.mark_complete(notes)
        else:
            habit.mark_complete_without_timer(notes)

        self._update_streak(habit)
        self._persist()
        return True

    def delete_habit(self, habit_id: int) -> bool:
        habit = self.get_habit_by_id(habit_id)
        if habit is None:
            return False
        self.habit_list.remove(habit)
        self._persist()
        return True

    def update_habit(self, habit_id: int, **kwargs) -> bool:        # Updates any habit attribute.
        habit = self.get_habit_by_id(habit_id)
        if habit is None:
            return False

        if "window_index" in kwargs:
            idx = kwargs.pop("window_index")
            label, start, end = TIME_WINDOWS[idx]
            kwargs["preferred_window"] = label
            kwargs["scheduled_start"]  = start
            kwargs["scheduled_end"]    = end

        habit.update_habit(**kwargs)
        self._persist()
        return True

    def get_habits(self) -> list: # Returns the full list of habits.
        return self.habit_list

    def get_habit_by_id(self, habit_id: int):        # Returns the Habit with the given ID, or None if not found.
        for habit in self.habit_list:
            if habit.habit_id == habit_id:
                return habit
        return None

    def reset_daily_statuses(self) -> None:
        for habit in self.habit_list:
            if habit.frequency == "daily":
                habit.status = "pending"
                habit.actual_start_time = None
                habit.actual_end_time   = None
        self._persist()

    def _update_streak(self, habit: Habit) -> None:
        streak = 0
        for entry in reversed(habit.completion_history):
            if entry.get("completed"):
                streak += 1
            else:
                break
        habit.current_streak = streak
        if streak > habit.longest_streak:
            habit.longest_streak = streak

    def _persist(self) -> None:        # Saves the current habit_list to disk immediately.
        self._storage.save_habits(self.habit_list)
