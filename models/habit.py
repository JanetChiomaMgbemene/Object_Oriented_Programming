from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


TIME_WINDOWS = [
    ("Early Morning",  "04:00", "06:00"),
    ("Morning",        "06:00", "09:00"),
    ("Mid-Morning",    "09:00", "12:00"),
    ("Afternoon",      "12:00", "15:00"),
    ("Late Afternoon", "15:00", "18:00"),
    ("Evening",        "18:00", "21:00"),
    ("Night",          "21:00", "23:59"),
    ("All Day",        "00:00", "23:59"),
]


def get_local_time(timezone_str: str) -> datetime:
    # Returns the current time as a timezone-aware datetime.
    try:
        tz = ZoneInfo(timezone_str)
    except (ZoneInfoNotFoundError, Exception):
        tz = ZoneInfo("UTC")
    return datetime.now(tz)


def format_time(dt: datetime) -> str:
    # 06:32 AM
    return dt.strftime("%I:%M %p")


def format_datetime(dt: datetime) -> str:
    # 2025-11-04 06:32 AM WAT
    return dt.strftime("%Y-%m-%d %I:%M %p %Z")


class Habit:
    def __init__(
        self,
        habit_id: int,
        habit_name: str,
        habit_type: str,
        preferred_window: str,
        scheduled_start: str,
        scheduled_end: str,
        frequency: str,
        reward: str,
        timezone: str = "UTC",
        status: str = "pending",
        custom_message: str = "",
        proof_image_path: str = None,
    ):
        self.habit_id         = habit_id
        self.habit_name       = habit_name
        self.habit_type       = habit_type        # "build" | "break"
        self.preferred_window = preferred_window
        self.scheduled_start  = scheduled_start
        self.scheduled_end    = scheduled_end
        self.frequency        = frequency         # "daily"|"weekly"|"monthly"
        self.reward           = reward
        self.timezone         = timezone
        self.status           = status            # "pending" | "complete"
        self.custom_message   = custom_message
        self.proof_image_path = proof_image_path

        self.actual_start_time: str | None = None
        self.actual_end_time:   str | None = None
        self._raw_start: datetime | None   = None  # internal, not saved to JSON

        self.current_streak: int = 0
        self.longest_streak: int = 0
        self.completion_history: list = []

    # Start the habit timer
    def start_habit(self) -> str:
        # Records the current local time as the actual start. Returns time string.
        now = get_local_time(self.timezone)
        self._raw_start       = now
        self.actual_start_time = format_time(now)
        return self.actual_start_time

    # Complete with timer (build habits)
    def mark_complete(self, notes: str = "") -> dict:
        # Records end time + duration, appends to history. Returns the log entry.
        now = get_local_time(self.timezone)
        self.actual_end_time = format_time(now)
        self.status = "complete"

        duration_mins = None
        if self._raw_start:
            delta = now - self._raw_start
            duration_mins = max(0, int(delta.total_seconds() / 60))

        entry = {
            "date":          now.strftime("%Y-%m-%d"),
            "actual_start":  self.actual_start_time,
            "actual_end":    self.actual_end_time,
            "duration_mins": duration_mins,
            "completed":     True,
            "proof":         self.proof_image_path,
            "notes":         notes,
            "timezone":      self.timezone,
        }
        self.completion_history.append(entry)
        return entry

    # Complete without timer (break habits / quick log)
    def mark_complete_without_timer(self, notes: str = "") -> dict:
        # Tick-off completion without Start/Done flow. Returns the log entry.
        now = get_local_time(self.timezone)
        self.actual_end_time = format_time(now)
        self.status = "complete"

        entry = {
            "date":          now.strftime("%Y-%m-%d"),
            "actual_start":  None,
            "actual_end":    self.actual_end_time,
            "duration_mins": None,
            "completed":     True,
            "proof":         self.proof_image_path,
            "notes":         notes,
            "timezone":      self.timezone,
        }
        self.completion_history.append(entry)
        return entry

    def upload_proof(self, image_path: str) -> None:
        self.proof_image_path = image_path
        if self.completion_history:
            self.completion_history[-1]["proof"] = image_path

    def update_habit(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> dict:
        return {
            "habit_id":          self.habit_id,
            "habit_name":        self.habit_name,
            "habit_type":        self.habit_type,
            "preferred_window":  self.preferred_window,
            "scheduled_start":   self.scheduled_start,
            "scheduled_end":     self.scheduled_end,
            "frequency":         self.frequency,
            "reward":            self.reward,
            "timezone":          self.timezone,
            "status":            self.status,
            "custom_message":    self.custom_message,
            "proof_image_path":  self.proof_image_path,
            "actual_start_time": self.actual_start_time,
            "actual_end_time":   self.actual_end_time,
            "current_streak":    self.current_streak,
            "longest_streak":    self.longest_streak,
            "completion_history":self.completion_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Habit":
        habit = cls(
            habit_id         = data["habit_id"],
            habit_name       = data["habit_name"],
            habit_type       = data["habit_type"],
            preferred_window = data.get("preferred_window", "Morning"),
            scheduled_start  = data.get("scheduled_start", "06:00"),
            scheduled_end    = data.get("scheduled_end",   "09:00"),
            frequency        = data["frequency"],
            reward           = data["reward"],
            timezone         = data.get("timezone", "UTC"),
            status           = data.get("status", "pending"),
            custom_message   = data.get("custom_message", ""),
            proof_image_path = data.get("proof_image_path"),
        )
        habit.actual_start_time  = data.get("actual_start_time")
        habit.actual_end_time    = data.get("actual_end_time")
        habit.current_streak     = data.get("current_streak", 0)
        habit.longest_streak     = data.get("longest_streak", 0)
        habit.completion_history = data.get("completion_history", [])
        return habit

    def __repr__(self) -> str:
        return (f"Habit(id={self.habit_id}, name='{self.habit_name}', "
                f"window='{self.preferred_window}', status={self.status}, "
                f"streak={self.current_streak})")