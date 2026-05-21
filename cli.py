import os
import sys
from datetime import date

from models.habit           import TIME_WINDOWS, get_local_time, format_datetime
from managers.storage_manager  import StorageManager
from managers.habit_manager    import HabitManager
from managers.timetable_manager import TimetableManager
from managers.default_habits   import DefaultHabitManager
from managers.reward_manager   import RewardManager
from managers.congrats_manager  import CongratManager
from analytics.analytics       import (
    generate_report, weakest_habits, strongest_habits,
    streak_at_risk, completion_rate, avg_duration,
)

TIMEZONE_OPTIONS = [
    ("Africa/Lagos",       "WAT  – Nigeria, Ghana, Cameroon"),
    ("Africa/Nairobi",     "EAT  – Kenya, Tanzania, Uganda"),
    ("Africa/Johannesburg","SAST – South Africa"),
    ("Europe/London",      "GMT/BST – United Kingdom"),
    ("Europe/Berlin",      "CET  – Germany, France, Italy"),
    ("America/New_York",   "EST  – US East Coast"),
    ("America/Los_Angeles","PST  – US West Coast"),
    ("Asia/Dubai",         "GST  – UAE"),
    ("Asia/Kolkata",       "IST  – India"),
    ("UTC",                "UTC  – Coordinated Universal Time"),
]


def clear():
    """Clears the terminal screen (works on Windows and Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str):
    """Prints a formatted section header."""
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def press_enter():
    input("\n  Press Enter to continue...")


def ask(prompt: str, default: str = "") -> str:
    response = input(f"  {prompt}").strip()
    return response if response else default


def ask_int(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        raw = ask(prompt)
        if raw.isdigit():
            val = int(raw)
            if min_val <= val <= max_val:
                return val
        print(f"  ⚠  Please enter a number between {min_val} and {max_val}.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = ask(prompt + " (y/n): ").lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  ⚠  Please type y or n.")



def choose_timezone() -> str:
    print_header("Welcome! Let's set your timezone.")
    print("  Your timezone is used to record the exact time you")
    print("  start and finish each habit.\n")

    for i, (tz, label) in enumerate(TIMEZONE_OPTIONS, start=1):
        print(f"  [{i:2}]  {label}")

    print(f"\n  [11]  Enter a custom timezone (e.g. America/Chicago)")
    choice = ask_int("Choose timezone: ", 1, 11)

    if choice == 11:
        custom = ask("Enter timezone string: ")
        return custom if custom else "UTC"
    return TIMEZONE_OPTIONS[choice - 1][0]



def menu_add_habit(hm: HabitManager, user_tz: str, defaults: DefaultHabitManager):
    """Guides the user through creating a new habit."""
    print_header("Add a New Habit")

    if ask_yes_no("Would you like to browse suggested habits?"):
        suggestions = defaults.get_suggestions()
        print("\n  Suggested habits:\n")
        for i, (name, htype, window, freq, reward) in enumerate(suggestions, 1):
            print(f"  [{i:2}]  {name:22}  ({htype}, {window}, {freq})")
        print(f"  [{len(suggestions)+1:2}]  Enter my own habit")

        pick = ask_int("Choose: ", 1, len(suggestions) + 1)

        if pick <= len(suggestions):
            name, htype, window_label, freq, reward = suggestions[pick - 1]
            window_index = next(
                i for i, (lbl, _, _) in enumerate(TIME_WINDOWS)
                if lbl == window_label
            )
            custom_msg = ask("Personal motivational message (optional, Enter to skip): ")
            habit = hm.add_habit(name, htype, window_index, freq, reward,
                                 user_tz, custom_msg)
            print(f"\n  ✓ '{habit.habit_name}' added!  Window: {habit.preferred_window}"
                  f"  ({habit.scheduled_start}–{habit.scheduled_end})")
            press_enter()
            return

    name = ask("Habit name: ")
    if not name:
        print("  ⚠  Name cannot be empty.")
        press_enter()
        return

    print("\n  Habit type:")
    print("  [1]  build  (do it more — e.g. Exercise, Read)")
    print("  [2]  break  (do it less — e.g. No Junk Food, No Late Scrolling)")
    htype = "build" if ask_int("Choose: ", 1, 2) == 1 else "break"

    print("\n  When do you want to do this habit?\n")
    for i, (label, start, end) in enumerate(TIME_WINDOWS, 1):
        print(f"  [{i}]  {label:15}  ({start} – {end})")

    window_index = ask_int("Choose a time window: ", 1, len(TIME_WINDOWS)) - 1

    print("\n  Frequency:")
    print("  [1] daily   [2] weekly   [3] monthly")
    freq_map = {1: "daily", 2: "weekly", 3: "monthly"}
    freq = freq_map[ask_int("Choose: ", 1, 3)]

    reward     = ask("Reward for completing it (e.g. Coffee ☕): ")
    custom_msg = ask("Personal motivational message (optional, Enter to skip): ")

    habit = hm.add_habit(name, htype, window_index, freq, reward, user_tz, custom_msg)

    chosen_label = TIME_WINDOWS[window_index][0]
    chosen_start = TIME_WINDOWS[window_index][1]
    chosen_end   = TIME_WINDOWS[window_index][2]
    print(f"\n  ✓ '{habit.habit_name}' added!")
    print(f"    Window : {chosen_label}  ({chosen_start} – {chosen_end})")
    print(f"    Reward : {reward}")
    press_enter()


def menu_start_habit(hm: HabitManager):
    print_header("Start a Habit")
    habits = hm.get_habits()
    pending = [h for h in habits if h.status == "pending" and not h.actual_start_time]

    if not pending:
        print("  All habits are either already started or completed today!")
        press_enter()
        return

    print("  Which habit are you starting right now?\n")
    for i, h in enumerate(pending, 1):
        print(f"  [{i}]  {h.habit_name:25}  {h.preferred_window}"
              f"  ({h.scheduled_start}–{h.scheduled_end})")

    print(f"  [{len(pending)+1}]  Cancel")
    choice = ask_int("Choose: ", 1, len(pending) + 1)
    if choice == len(pending) + 1:
        return

    habit   = pending[choice - 1]
    recorded = hm.start_habit(habit.habit_id)
    print(f"\n  ▶  Started '{habit.habit_name}' at {recorded}")
    print(f"     Press 'Done' when you finish to record your end time.")
    press_enter()


def menu_mark_done(hm: HabitManager, cm: CongratManager, rm: RewardManager):
    print_header("Mark Habit as Done ✓")
    habits = hm.get_habits()

    markable = [h for h in habits if h.status != "complete"]

    if not markable:
        print("  All habits are already completed for today! 🎉")
        press_enter()
        return

    print("  Which habit did you just finish?\n")
    for i, h in enumerate(markable, 1):
        state = "▶ in progress" if h.actual_start_time else "○ pending"
        start_info = f" (started {h.actual_start_time})" if h.actual_start_time else ""
        print(f"  [{i}]  {h.habit_name:25}  {state}{start_info}")

    print(f"  [{len(markable)+1}]  Cancel")
    choice = ask_int("Choose: ", 1, len(markable) + 1)
    if choice == len(markable) + 1:
        return

    habit = markable[choice - 1]
    notes = ask("Add a note (optional, Enter to skip): ")

    # Break habits don't use Start/Done timer
    use_timer = habit.habit_type == "build" and bool(habit.actual_start_time)
    hm.mark_complete(habit.habit_id, notes, use_timer)

    # Refresh to get updated streak
    habit = hm.get_habit_by_id(habit.habit_id)

    print(f"\n  ✓ '{habit.habit_name}' marked complete!")
    if habit.actual_start_time and habit.actual_end_time:
        print(f"    Started : {habit.actual_start_time}")
        print(f"    Finished: {habit.actual_end_time}")
        if habit.completion_history:
            dur = habit.completion_history[-1].get("duration_mins")
            if dur is not None:
                print(f"    Duration: {dur} minutes")

    print(f"    Streak  : {habit.current_streak} 🔥")
    print(f"\n  {cm.get_custom_message(habit)}")

    # Ask about proof upload
    if ask_yes_no("\n  Upload a proof photo?"):
        path = ask("Image file path: ")
        if rm.verify_proof(path):
            hm.get_habit_by_id(habit.habit_id).upload_proof(path)
            print("  ✓ Proof saved!")
        else:
            print("  ⚠  File not found or not a valid image.")

    press_enter()



def menu_view_timetable(tm: TimetableManager, user_tz: str):
    print_header("Today's Timetable")
    now = get_local_time(user_tz)
    print(f"  Current time: {format_datetime(now)}\n")
    print(tm.display_timetable())
    press_enter()


def menu_analytics(hm: HabitManager):
    print_header("Analytics & Progress")
    habits = hm.get_habits()

    if not habits:
        print("  No habits to analyse yet.")
        press_enter()
        return

    report = generate_report(habits)

    print(f"  Total habits       : {report['total_habits']}")
    print(f"  Build habits       : {report['build_habits']}")
    print(f"  Break habits       : {report['break_habits']}")
    print(f"  Avg completion rate: {report['avg_completion_rate']*100:.1f}%")
    print(f"  Longest streak ever: {report['longest_overall_streak']} days")
    print(f"  Most consistent    : {report['most_consistent']}")
    print(f"  Needs improvement  : {report['needs_improvement']}")
    if report["avg_duration_mins"] is not None:
        print(f"  Avg actual duration: {report['avg_duration_mins']} min")

    # Per-habit breakdown
    print("\n  ── Per-habit breakdown ──────────────────────────────────────")
    for h in habits:
        rate  = completion_rate(h)
        dur   = avg_duration(h)
        dur_s = f"  avg {dur} min" if dur else ""
        print(f"  {h.habit_name:25}  {rate*100:5.1f}%  streak {h.current_streak}{dur_s}")

    # Streak at risk
    at_risk = streak_at_risk(habits)
    if at_risk:
        print("\n  ⚠  STREAK ALERT — do these today or lose your streak:")
        for h in at_risk:
            print(f"     • {h.habit_name} ({h.current_streak}-day streak at risk!)")

    press_enter()


def menu_manage(hm: HabitManager):
    """Edit or delete existing habits."""
    print_header("Manage Habits")
    habits = hm.get_habits()

    if not habits:
        print("  No habits yet.")
        press_enter()
        return

    for h in habits:
        print(f"  [ID {h.habit_id}]  {h.habit_name:25}  {h.preferred_window}"
              f"  {h.frequency}  streak {h.current_streak}")

    habit_id = ask_int("\n  Enter habit ID to edit/delete (0 to cancel): ", 0, 9999)
    if habit_id == 0:
        return

    habit = hm.get_habit_by_id(habit_id)
    if not habit:
        print("  ⚠  Habit not found.")
        press_enter()
        return

    print(f"\n  Editing: {habit.habit_name}")
    print("  [1] Change name")
    print("  [2] Change time window")
    print("  [3] Change reward")
    print("  [4] Change custom message")
    print("  [5] Delete this habit")
    print("  [6] Cancel")

    action = ask_int("Choose: ", 1, 6)

    if action == 1:
        new_name = ask("New name: ")
        hm.update_habit(habit_id, habit_name=new_name)
        print("  ✓ Name updated.")

    elif action == 2:
        print("\n  Choose a new time window:\n")
        for i, (label, start, end) in enumerate(TIME_WINDOWS, 1):
            print(f"  [{i}]  {label:15}  ({start} – {end})")
        idx = ask_int("Choose: ", 1, len(TIME_WINDOWS)) - 1
        hm.update_habit(habit_id, window_index=idx)
        print(f"  ✓ Window updated to '{TIME_WINDOWS[idx][0]}'.")

    elif action == 3:
        new_reward = ask("New reward: ")
        hm.update_habit(habit_id, reward=new_reward)
        print("  ✓ Reward updated.")

    elif action == 4:
        new_msg = ask("New motivational message: ")
        hm.update_habit(habit_id, custom_message=new_msg)
        print("  ✓ Message updated.")

    elif action == 5:
        if ask_yes_no(f"  Are you sure you want to delete '{habit.habit_name}'?"):
            hm.delete_habit(habit_id)
            print("  ✓ Habit deleted.")

    press_enter()


def main():

    storage  = StorageManager()
    hm       = HabitManager(storage)
    hm.load()

    tm       = TimetableManager(hm)
    defaults = DefaultHabitManager()
    rm       = RewardManager()
    cm       = CongratManager()

    settings_file = "data/settings.txt"
    if os.path.exists(settings_file):
        with open(settings_file) as f:
            user_tz = f.read().strip() or "UTC"
    else:
        clear()
        user_tz = choose_timezone()
        os.makedirs("data", exist_ok=True)
        with open(settings_file, "w") as f:
            f.write(user_tz)
        print(f"\n  ✓ Timezone set to: {user_tz}")
        press_enter()

    if not hm.get_habits():
        if ask_yes_no("\n  No habits found. Load sample data for demonstration?"):
            seed_habits = defaults.get_four_week_seed(user_tz)
            for h in seed_habits:
                hm.habit_list.append(h)
            hm._next_id = len(seed_habits) + 1
            hm._persist()
            print("  ✓ Sample data loaded.")
            press_enter()

    reset_file = "data/last_reset.txt"
    today_str  = date.today().isoformat()
    if os.path.exists(reset_file):
        with open(reset_file) as f:
            last_reset = f.read().strip()
        if last_reset != today_str:
            hm.reset_daily_statuses()
            with open(reset_file, "w") as f:
                f.write(today_str)
    else:
        with open(reset_file, "w") as f:
            f.write(today_str)

    while True:
        clear()
        now = get_local_time(user_tz)

        print("\n" + "═" * 60)
        print("   🗓  HABIT TRACKER".center(60))
        print(f"   {format_datetime(now)}".center(60))
        print("═" * 60)

        habits = hm.get_habits()
        done   = sum(1 for h in habits if h.status == "complete")
        total  = len(habits)
        print(f"\n   Progress today: {done}/{total} habits complete\n")

        at_risk = streak_at_risk(habits)
        if at_risk:
            names = ", ".join(h.habit_name for h in at_risk)
            print(f"   ⚠  Streak alert: {names}\n")

        print("  [1]  View timetable")
        print("  [2]  Start a habit  (records start time ▶)")
        print("  [3]  Mark habit done  (records end time ✓)")
        print("  [4]  Add a new habit")
        print("  [5]  Analytics & progress")
        print("  [6]  Manage habits (edit / delete)")
        print("  [7]  Exit")
        print()

        choice = ask_int("Choose an option: ", 1, 7)

        if   choice == 1: menu_view_timetable(tm, user_tz)
        elif choice == 2: menu_start_habit(hm)
        elif choice == 3: menu_mark_done(hm, cm, rm)
        elif choice == 4: menu_add_habit(hm, user_tz, defaults)
        elif choice == 5: menu_analytics(hm)
        elif choice == 6: menu_manage(hm)
        elif choice == 7:
            print("\n  👋 Goodbye! Keep up those habits!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()