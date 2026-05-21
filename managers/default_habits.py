import random
from datetime import date, timedelta, datetime
from models.habit import Habit, TIME_WINDOWS


WINDOW_LOOKUP = {label: (start, end) for label, start, end in TIME_WINDOWS}


class DefaultHabitManager:
    def __init__(self):        # Templates: (name, type, window_label, frequency, reward)
        self._templates = {
            "daily": [
                ("Drink Water",       "build", "Morning",       "daily",   "Refreshed feeling 💧"),
                ("Morning Exercise",  "build", "Morning",       "daily",   "Energy boost 🏃"),
                ("Read 30 Minutes",   "build", "Night",         "daily",   "New knowledge 📚"),
                ("No Junk Food",      "break", "All Day",       "daily",   "Healthier body 🥗"),
                ("Meditate",          "build", "Early Morning", "daily",   "Inner calm 🧘"),
                ("No Late Scrolling", "break", "Night",         "daily",   "Better sleep 😴"),
            ],
            "weekly": [
                ("Weekly Goal Review","build", "Mid-Morning",   "weekly",  "Clarity & focus 🎯"),
                ("Deep Work Session", "build", "Morning",       "weekly",  "Progress on goals 💡"),
            ],
            "monthly": [
                ("Review Finances",   "build", "Mid-Morning",   "monthly", "Financial control 💰"),
                ("Skill Practice",    "build", "Afternoon",     "monthly", "Personal growth 🌱"),
            ],
        }

    def get_suggestions(self, frequency: str = None) -> list:
        if frequency and frequency in self._templates:
            return self._templates[frequency]
        all_suggestions = []
        for lst in self._templates.values():
            all_suggestions.extend(lst)
        return all_suggestions

    def get_four_week_seed(self, timezone: str = "UTC") -> list:
        today      = date.today()
        start_date = today - timedelta(days=27)        # (habit_id, name, type, window, frequency, reward)
        seeds = [
            (1, "Morning Exercise", "build", "Morning",  "daily",  "Energy boost 🏃"),
            (2, "Drink Water",      "build", "Morning",  "daily",  "Refreshed 💧"),
            (3, "Read 30 Minutes",  "build", "Night",    "daily",  "Knowledge 📚"),
            (4, "No Junk Food",     "break", "All Day",  "daily",  "Healthier 🥗"),
            (5, "Weekly Review",    "build", "Mid-Morning","weekly","Clarity 🎯"),
        ]

        # Which day offsets (0=28 days ago … 27=today) were MISSED per habit
        miss_offsets = {
            1: [14],
            2: [8, 9, 20, 22],
            3: [5, 12, 18, 19, 24, 25],
            4: [1, 6, 9, 11, 13, 15, 17, 19, 21, 24, 26],
            5: [14],   # missed week 3 Monday
        }

        habits = []

        for (hid, name, htype, window, freq, reward) in seeds:
            sched_start, sched_end = WINDOW_LOOKUP.get(window, ("06:00", "09:00"))

            habit = Habit(
                habit_id         = hid,
                habit_name       = name,
                habit_type       = htype,
                preferred_window = window,
                scheduled_start  = sched_start,
                scheduled_end    = sched_end,
                frequency        = freq,
                reward           = reward,
                timezone         = timezone,
            )

            # Determine which days to create entries for
            if freq == "weekly":
                # Only Mondays in the 28-day window
                day_offsets = [
                    i for i in range(28)
                    if (start_date + timedelta(days=i)).weekday() == 0
                ]
            else:
                day_offsets = list(range(28))

            for offset in day_offsets:
                entry_date = start_date + timedelta(days=offset)
                completed  = offset not in miss_offsets.get(hid, [])

                if completed:
                    sim_start, sim_end, duration = self._simulate_times(
                        sched_start, sched_end, htype
                    )
                else:
                    sim_start = sim_end = None
                    duration  = None

                entry = {
                    "date":          entry_date.isoformat(),
                    "actual_start":  sim_start,
                    "actual_end":    sim_end,
                    "duration_mins": duration,
                    "completed":     completed,
                    "proof":         None,
                    "notes":         "Seed data" if completed else "",
                    "timezone":      timezone,
                }
                habit.completion_history.append(entry)

            # Calculate streak from history
            streak = 0
            for entry in reversed(habit.completion_history):
                if entry["completed"]:
                    streak += 1
                else:
                    break
            habit.current_streak = streak
            habit.longest_streak = streak

            # Today's status
            if habit.completion_history and habit.completion_history[-1]["completed"]:
                habit.status = "complete"
                habit.actual_start_time = habit.completion_history[-1]["actual_start"]
                habit.actual_end_time   = habit.completion_history[-1]["actual_end"]

            habits.append(habit)

        return habits

    def _simulate_times(
        self, sched_start: str, sched_end: str, habit_type: str
    ) -> tuple:
        if habit_type == "break":            # Break habits just get a tick at the end of the day
            return None, "11:59 PM", None

        h_start, m_start = map(int, sched_start.split(":"))
        h_end,   m_end   = map(int, sched_end.split(":"))

        window_mins = (h_end * 60 + m_end) - (h_start * 60 + m_start)
        if window_mins <= 0:
            window_mins = 60

        start_offset = random.randint(0, max(0, int(window_mins * 0.66)))
        abs_start    = h_start * 60 + m_start + start_offset

        # Random duration 5–45 minutes (capped at window end)
        duration     = random.randint(5, 45)
        abs_end      = min(abs_start + duration, h_end * 60 + m_end)
        duration     = abs_end - abs_start

        # Format back to readable strings
        def mins_to_str(total_mins):
            h = (total_mins // 60) % 24
            m = total_mins % 60
            period = "AM" if h < 12 else "PM"
            h12    = h % 12 or 12
            return f"{h12:02d}:{m:02d} {period}"

        return mins_to_str(abs_start), mins_to_str(abs_end), duration