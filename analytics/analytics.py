from functools import reduce
from datetime import date, timedelta


def calc_streak(habit) -> tuple:
    if not habit.completion_history:
        return (0, 0)
    current = 0
    for entry in reversed(habit.completion_history):
        if entry.get("completed"):
            current += 1
        else:
            break
    longest, run = 0, 0
    for entry in habit.completion_history:
        if entry.get("completed"):
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return (current, longest)


def update_streaks(habit_list: list) -> list:
    def recalc(habit):
        current, longest = calc_streak(habit)
        habit.current_streak = current
        habit.longest_streak = longest
        return habit
    return list(map(recalc, habit_list))


def completion_rate(habit, days: int = 28) -> float:
    if not habit.completion_history:
        return 0.0
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    recent = [e for e in habit.completion_history if e.get("date", "") >= cutoff]
    if not recent:
        return 0.0
    return round(sum(1 for e in recent if e.get("completed")) / len(recent), 3)


def filter_by_type(habit_list: list, habit_type: str) -> list:
    return list(filter(lambda h: h.habit_type == habit_type, habit_list))


def filter_by_frequency(habit_list: list, frequency: str) -> list:
    return list(filter(lambda h: h.frequency == frequency, habit_list))


def filter_by_window(habit_list: list, window: str) -> list:
    return list(filter(lambda h: h.preferred_window == window, habit_list))


def filter_completed_today(habit_list: list) -> list:
    today = date.today().isoformat()
    def done_today(h):
        return any(e.get("date") == today and e.get("completed")
                   for e in h.completion_history)
    return list(filter(done_today, habit_list))


def weakest_habits(habit_list: list, n: int = 3) -> list:
    return sorted(habit_list, key=lambda h: completion_rate(h))[:n]


def strongest_habits(habit_list: list, n: int = 3) -> list:
    return sorted(habit_list, key=lambda h: completion_rate(h), reverse=True)[:n]


def streak_at_risk(habit_list: list) -> list:
    today = date.today().isoformat()
    def at_risk(h):
        if h.current_streak == 0:
            return False
        return not any(e.get("date") == today and e.get("completed")
                       for e in h.completion_history)
    return list(filter(at_risk, habit_list))


def avg_duration(habit):
    durations = [e["duration_mins"] for e in habit.completion_history
                 if e.get("duration_mins") is not None]
    return round(sum(durations) / len(durations), 1) if durations else None

def get_all_habits(habit_list: list) -> list:
    return list(habit_list)


def get_habits_by_periodicity(habit_list: list, periodicity: str) -> list:
    return list(filter(lambda h: h.frequency == periodicity, habit_list))


def longest_streak_all(habit_list: list) -> tuple:
    if not habit_list:
        return ("None", 0)
    best = max(habit_list, key=lambda h: h.longest_streak)
    return (best.habit_name, best.longest_streak)


def longest_streak_for_habit(habit) -> int:
    _, longest = calc_streak(habit)
    return longest


def generate_report(habit_list: list) -> dict:
    if not habit_list:
        return {"total_habits": 0, "build_habits": 0, "break_habits": 0,
                "avg_completion_rate": 0.0, "longest_overall_streak": 0,
                "most_consistent": "N/A", "needs_improvement": "N/A",
                "avg_duration_mins": None}

    def accumulate(acc, habit):
        acc["total_habits"]    += 1
        acc["build_habits"]    += int(habit.habit_type == "build")
        acc["break_habits"]    += int(habit.habit_type == "break")
        acc["total_rate"]      += completion_rate(habit)
        acc["longest_streak"]   = max(acc["longest_streak"], habit.longest_streak)
        dur = avg_duration(habit)
        if dur is not None:
            acc["dur_sum"]   += dur
            acc["dur_count"] += 1
        return acc

    totals = reduce(accumulate, habit_list,
                    {"total_habits":0,"build_habits":0,"break_habits":0,
                     "total_rate":0.0,"longest_streak":0,"dur_sum":0.0,"dur_count":0})

    n = totals["total_habits"]
    ranked = sorted(habit_list, key=lambda h: completion_rate(h))
    avg_dur = (round(totals["dur_sum"] / totals["dur_count"], 1)
               if totals["dur_count"] else None)

    return {
        "total_habits":           n,
        "build_habits":           totals["build_habits"],
        "break_habits":           totals["break_habits"],
        "avg_completion_rate":    round(totals["total_rate"] / n, 3),
        "longest_overall_streak": totals["longest_streak"],
        "most_consistent":        ranked[-1].habit_name if ranked else "N/A",
        "needs_improvement":      ranked[0].habit_name  if ranked else "N/A",
        "avg_duration_mins":      avg_dur,
    }