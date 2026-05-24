#  Timetable-Based Habit Tracking Application
## 1. Project Overview
Habit Tracker is a simple application built using Python and object-oriented programming (OOP) concepts.
This is a Python-based habit tracking application that organises habits into a
timetable format rather than a plain checklist. Instead of showing habits as
a flat list, the app groups them by time window (e.g. Morning, Evening) so
users can see their daily schedule at a glance.

When a user starts or finishes a habit, the app automatically records the
exact local clock time in their timezone (no manual time entry required).
This means the timetable shows not just when a habit was planned, but when
it actually happened.

The application is available in two modes:

| Mode | File to run | Best for |
|---|---|---|
| CLI (Command-Line Interface) | `main.py` | Terminal users, coursework submission |
| GUI (Graphical User Interface) | `gui/gui_manager.py` | Visual interaction, daily use |

---

## 2. Features

- Time window picker - choose Morning, Evening, etc. instead of typing a time
- Auto-recorded times - the app logs the exact clock time you press Start and Done
- Duration tracking - automatically calculates how long each habit took
- Timezone support - works correctly for users in any timezone worldwide
- Streak tracking - counts consecutive completions and alerts you when a streak is at risk
- Proof upload - attach a photo as evidence of completing a habit
- Motivational messages - personalised congratulatory messages on completion
- Rewards system - assign a reward to each habit
- Analytics - completion rates, streaks, weakest habits, average duration
- Predefined habits - browse built-in suggestions to get started quickly
- 4-week sample data - load realistic dummy data for testing and demonstration
- JSON persistence - all data is saved to disk and reloaded between sessions
- No internet required - fully offline, no third-party packages needed

---

## 3. Requirements

| Requirement | Details |
|---|---|
| Python version | *3.9 or higher* (3.12 recommended) |
| External packages | None — uses only the Python standard library |
| Operating system | Windows, macOS, or Linux |
| GUI dependency | Tkinter (included with most Python installations) |

> Why Python 3.9+?  
> This project uses `zoneinfo`, a timezone library that was added to the Python
> standard library in version 3.9. No `pip install` is needed.

### Checking your Python version

```bash
python3 --version
```

If you see `Python 3.9.x` or higher, you are ready to go.

### Checking Tkinter (for the GUI only)

```bash
python3 -m tkinter
```

A small test window should appear. If it does, Tkinter is installed. If not,
see the note below.

> Tkinter not found?    
> On Windows: reinstall Python from python.org and tick the "tcl/tk" option.

---

## 4. Installation

No installation is required. Simply download or unzip the project folder.

```bash
# If you received the project as a zip file, unzip it first:
unzip habit_tracker.zip

# Move into the project folder:
cd habit_tracker
```

That is all. There is nothing to install with `pip`.

---

## 5. How to Run

### Run the CLI (recommended for coursework)

```bash
python3 main.py
```

### Run the GUI

```bash
python3 gui/gui_manager.py
```

Both modes share the same data files (`data/habits.json`), so anything you do
in the CLI is immediately visible in the GUI and vice versa.

---

## 6. First Launch

The very first time you run the app, it will ask you to "choose your timezone".
This is a one-time setup step.

CLI — timezone picker:

```
══════════════════════════════════════════════════
  Welcome! Let's set your timezone.
══════════════════════════════════════════════════

  [ 1]  WAT  – Nigeria, Ghana, Cameroon
  [ 2]  EAT  – Kenya, Tanzania, Uganda
  [ 3]  SAST – South Africa
  [ 4]  GMT/BST – United Kingdom
  ...
  [10]  UTC  – Coordinated Universal Time
  [11]  Enter a custom timezone

Choose timezone: 1
✓ Timezone set to: Africa/Lagos
```

GUI — timezone picker:  
A screen with radio buttons appears. Select your region and click
Confirm & Continue.

After choosing your timezone, the app will offer to load sample data - 5
pre-built habits with 4 weeks of realistic history. This is useful for
exploring the app before creating your own habits.

Your timezone is saved to `data/settings.txt` and will not be asked again.

---

## 7. Using the CLI

After the first-launch setup, the main menu is displayed on every run:

```
════════════════════════════════════════════════════════════
              🗓  HABIT TRACKER
         2025-11-04 07:15 AM WAT
════════════════════════════════════════════════════════════

   Progress today: 1/5 habits complete

   ⚠  Streak alert: Morning Exercise, Drink Water

  [1]  View timetable
  [2]  Start a habit  (records start time ▶)
  [3]  Mark habit done  (records end time ✓)
  [4]  Add a new habit
  [5]  Analytics & progress
  [6]  Manage habits (edit / delete)
  [7]  Exit
```

### Adding a habit

Select `[4]` and follow the prompts. When asked for a time, you will see a
"numbered window menu" instead of a text box:

```
  When do you want to do this habit?

  [1]  Early Morning   (04:00 – 06:00)
  [2]  Morning         (06:00 – 09:00)
  [3]  Mid-Morning     (09:00 – 12:00)
  [4]  Afternoon       (12:00 – 15:00)
  [5]  Late Afternoon  (15:00 – 18:00)
  [6]  Evening         (18:00 – 21:00)
  [7]  Night           (21:00 – 23:59)
  [8]  All Day         (00:00 – 23:59)

Choose a time window: 2
```

### Starting and finishing a habit

```
# Press Start when you begin:
[2]  Start a habit
→ ▶  Started 'Morning Exercise' at 06:32 AM

# Press Done when you finish:
[3]  Mark habit done
→ ✓  'Morning Exercise' marked complete!
     Started : 06:32 AM
     Finished: 07:01 AM
     Duration: 29 minutes
     Streak  : 8 🔥

     Great job completing 'Morning Exercise'! (8-day streak! 🔥)
     Consistency is key and you have it! 🏆
```

### Viewing the timetable

```
[1]  View timetable

┌────────────────────────────────────────────────────────────────┐
│                     HABIT TIMETABLE                            │
├────────────────────┬──────────────────────┬───────┬────────────┤
│ Window             │ Habit                │ Type  │ Status     │
├────────────────────┼──────────────────────┼───────┼────────────┤
│ Morning            │ Morning Exercise     │ build │ ✓ complete │
│ 06:00 – 09:00      │ ↳ 06:32 AM → 07:01 AM 29 min│       │            │
├────────────────────┼──────────────────────┼───────┼────────────┤
│ Morning            │ Drink Water          │ build │ ▶ in progr │
│ 06:00 – 09:00      │ ↳ Started 07:05 AM   │       │            │
├────────────────────┼──────────────────────┼───────┼────────────┤
│ Night              │ Read 30 Minutes      │ build │ ○ pending  │
│ 21:00 – 23:59      │                      │       │            │
└────────────────────┴──────────────────────┴───────┴────────────┘
```

### Analytics

```
[5]  Analytics & progress

  Total habits       : 5
  Build habits       : 4
  Break habits       : 1
  Avg completion rate: 78.4%
  Longest streak ever: 27 days
  Most consistent    : Morning Exercise
  Needs improvement  : No Junk Food
  Avg actual duration: 31.2 min

  ── Per-habit breakdown ─────────────────────────────────────────
  Morning Exercise          96.4%  streak 8
  Drink Water               89.3%  streak 5
  Read 30 Minutes           78.6%  streak 3
  No Junk Food              60.7%  streak 0
  Weekly Review             75.0%  streak 1
```

---

## 8. Using the GUI

Launch the GUI with:

```bash
python3 gui/gui_manager.py
```

### Screen guide

| Screen | How to reach it | What it does |
|---|---|---|
| Timezone Setup | Automatic on first run | Choose your local timezone |
| Main Dashboard | Home screen | Progress bar, streak alerts, quick habit list |
| Timetable | "View Timetable" button | Grid of all habits; Start / Done buttons |
| Add Habit | "Add New Habit" button | Form with window dropdown (no typed times) |
| Habit Detail | "Details" on any habit | Full stats, history table, proof upload |
| Analytics | "Analytics" button | Summary report and per-habit breakdown |
| Manage Habits | "Manage Habits" button | Edit name/window/reward, or delete |

### Key GUI interactions

- Start button (▶) - click when you begin a habit; records the real clock time
- Done button (✓) - click when you finish; records end time and calculates duration
- Upload Proof - opens a file picker to attach a photo (jpg, png, etc.)
- Details - opens a full history table showing actual start/end times per entry
- The clock in the top-right corner updates every second in your local timezone
---

## 9. Project Structure

```
habit_tracker/
│
├── main.py                       # Entry point for the CLI
│
├── cli.py                        # Full command-line interface
│
├── models/
│   ├── __init__.py
│   └── habit.py                  # Habit class + TIME_WINDOWS + timezone helpers
│
├── managers/
│   ├── __init__.py
│   ├── habit_manager.py          # CRUD controller for all habits
│   ├── storage_manager.py        # JSON read/write (save & load)
│   ├── default_habits.py         # Predefined habits + 4-week seed data
│   ├── timetable_manager.py      # Sorts and displays habits by time window
│   ├── reward_manager.py         # Reward assignment + proof verification
│   └── congrat_manager.py        # Motivational message generation
│
├── analytics/
│   ├── __init__.py
│   └── analytics.py              # Functional programming: map/filter/reduce stats
│
├── gui/
│   ├── __init__.py
│   └── gui_manager.py            # Full Tkinter GUI (7 screens)
│
├── tests/
│   ├── __init__.py
│   ├── test_habit.py             # Unit tests for Habit class
│   ├── test_storage_manager.py   # Unit tests for StorageManager
│   ├── test_habit_manager.py     # Unit tests for HabitManager
│   ├── test_timetable_manager.py # Unit tests for TimetableManager
│   ├── test_default_habits.py    # Unit tests for DefaultHabitManager
│   ├── test_reward_manager.py    # Unit tests for RewardManager
│   ├── test_congrat_manager.py   # Unit tests for CongratManager
│   └── test_analytics.py        # Unit tests for all analytics functions
│
├── data/
│   ├── habits.json               # Auto-created; stores all habit data
│   ├── settings.txt              # Auto-created; stores your timezone
│   └── last_reset.txt            # Auto-created; tracks daily status resets
│
├── uploads/                      # Auto-created; stores proof images
│
├── requirements.txt              # No installs needed (standard library only)
└── README.md                     # This file
```
---

## 10. Module Descriptions

### `models/habit.py`
The core data structure. Every habit is an instance of the `Habit` class.

Key attributes:
- `preferred_window` — the time slot the user chose (e.g. `"Morning"`)
- `scheduled_start` / `scheduled_end` — the window boundaries (e.g. `"06:00"`, `"09:00"`)
- `actual_start_time` / `actual_end_time` — the real clock times recorded automatically
- `completion_history` — a list of log entries, one per completion

Key methods:
- `start_habit()` — records the current local time as the actual start
- `mark_complete()` — records end time, calculates duration, appends to history
- `mark_complete_without_timer()` — for break habits that don't use Start/Done
- `to_dict()` / `from_dict()` — converts to/from plain dict for JSON storage

---

### `managers/habit_manager.py`
The central controller. All other parts of the app communicate with habits
through this class.

Key methods:
- `load()` — loads habits from JSON on startup
- `add_habit()` — creates a new habit using a window index (not raw times)
- `start_habit()` — calls `habit.start_habit()` and saves to disk
- `mark_complete()` — calls `habit.mark_complete()` or `mark_complete_without_timer()`
- `delete_habit()` / `update_habit()` — remove or change a habit
- `reset_daily_statuses()` — resets all daily habits to "pending" each morning

---

### `managers/storage_manager.py`
Handles all reading and writing to `data/habits.json`. No other module
touches the file directly.

Key methods:
- `save_habits(habit_list)` — serialises Habit objects to JSON and writes to disk
- `load_habits()` — reads JSON and deserialises back to Habit objects

---

### `managers/timetable_manager.py`
Sorts and groups habits into a time-slot grid.

Key methods:
- `organise_habits()` — sorts by `scheduled_start`, groups by window label
- `get_timetable()` — returns the grouped structure
- `display_timetable()` — returns a formatted ASCII string for the CLI

---

### `managers/default_habits.py`
Provides built-in habit suggestions and the 4-week test dataset.

Key methods:
- `get_suggestions(frequency)` — returns predefined habit templates
- `get_four_week_seed(timezone)` — returns 5 habits with 28 days of realistic history, including simulated actual start/end times

---

### `managers/reward_manager.py`
Manages rewards and proof image verification.

Key methods:
- `assign_reward(habit)` — returns the habit's reward or picks a default one
- `verify_proof(image_path)` — checks the file exists and has a valid image extension

---

### `managers/congrat_manager.py`
Generates motivational messages on habit completion.

Key methods:
- `generate_message(habit)` — personalised message with habit name and streak count
- `get_random_message()` — a random message with no context needed
- `get_custom_message(habit)` — returns the user's custom message if set

---

### `analytics/analytics.py`
All analytics functions are pure functions following Functional Programming
principles: given the same input they always return the same output, and they
never modify any Habit objects.

| Function | FP technique | Description |
|---|---|---|
| `calc_streak(habit)` | Iteration | Returns (current, longest) streak |
| `update_streaks(habit_list)` | `map()` | Recalculates streaks for every habit |
| `completion_rate(habit)` | Aggregation | Fraction of completions in last N days |
| `filter_by_type()` | `filter()` | Returns only build or break habits |
| `filter_by_window()` | `filter()` | Returns habits in a specific time window |
| `filter_completed_today()` | `filter()` | Returns habits done today |
| `weakest_habits()` | `sorted()` + `lambda` | N habits with lowest completion rate |
| `strongest_habits()` | `sorted()` + `lambda` | N habits with highest completion rate |
| `streak_at_risk()` | `filter()` | Habits with active streak not yet done today |
| `avg_duration(habit)` | Aggregation | Average actual duration in minutes |
| `generate_report()` | `reduce()` | Full summary dict across all habits |

---

### `gui/gui_manager.py`
The full Tkinter GUI with 7 screens. Built with `tkinter` and `tkinter.ttk`
which are part of the Python standard library.

Screens:
1. `TimezoneScreen` — first-launch timezone picker
2. `MainScreen` — dashboard with progress bar and streak alerts
3. `TimetableScreen` — habit grid with Start / Done action buttons
4. `AddHabitScreen` — new habit form with time window dropdown
5. `HabitDetailScreen` — full detail, history table, proof upload
6. `AnalyticsScreen` — summary stats and per-habit breakdown
7. `ManageScreen` — edit and delete habits

---

## 11. How Time Recording Works

This is one of the most important design decisions in the project.

### Old approach (removed)
The user typed a fixed start time (e.g. `"06:00"`) and a fixed end time
(e.g. `"07:00"`) when creating a habit. These times never changed, regardless
of when the user actually did the habit.

### New approach
The user chooses a 'time window' (e.g. "Morning: 06:00–09:00") when
creating a habit. This window represents their intention — when they
plan to do it.

When they actually do the habit:

1. They press "Start" → the app calls `habit.start_habit()` which records
   `datetime.now(ZoneInfo(user_timezone))` as `actual_start_time`
2. They press "Done" → the app calls `habit.mark_complete()` which records
   the end time and calculates `duration_mins = end - start`

Both times are stored in the `completion_history` log entry:

```json
{
  "date":          "2025-11-04",
  "actual_start":  "06:32 AM",
  "actual_end":    "07:01 AM",
  "duration_mins": 29,
  "completed":     true,
  "proof":         null,
  "notes":         "Felt great today",
  "timezone":      "Africa/Lagos"
}
```

This means:
- The timetable always shows real times, not planned ones
- The analytics can report average actual duration
- The user never has to type a time manually

### Timezone handling
Timezones are handled using Python's built-in `zoneinfo` module (Python 3.9+).
The user's timezone string (e.g. `"Africa/Lagos"`) is stored in
`data/settings.txt` and embedded in every habit and every log entry.
This means even if a user travels, their historical data correctly reflects
the timezone they were in at the time.

---

## 12. Data Storage

All habit data is stored in a single human-readable JSON file:
`data/habits.json`

### Example record

```json
[
  {
    "habit_id": 1,
    "habit_name": "Morning Exercise",
    "habit_type": "build",
    "preferred_window": "Morning",
    "scheduled_start": "06:00",
    "scheduled_end": "09:00",
    "frequency": "daily",
    "reward": "Energy boost 🏃",
    "timezone": "Africa/Lagos",
    "status": "complete",
    "custom_message": "",
    "proof_image_path": null,
    "actual_start_time": "06:32 AM",
    "actual_end_time": "07:01 AM",
    "current_streak": 8,
    "longest_streak": 27,
    "completion_history": [
      {
        "date": "2025-11-04",
        "actual_start": "06:32 AM",
        "actual_end": "07:01 AM",
        "duration_mins": 29,
        "completed": true,
        "proof": null,
        "notes": "",
        "timezone": "Africa/Lagos"
      }
    ]
  }
]
```

### Other data files

| File | Purpose | Created by |
|---|---|---|
| `data/habits.json` | All habit data | `StorageManager` on first save |
| `data/settings.txt` | User's timezone string | CLI / GUI on first launch |
| `data/last_reset.txt` | Date of last daily reset | CLI on startup |

> Backup tip: To back up your data, simply copy the `data/` folder.
> To start fresh, delete `data/habits.json`.

---

## 13. Running the Tests

The test suite uses Python's built-in `unittest` module — nothing to install.

### Run all tests

```bash
cd habit_tracker
python3 -m unittest discover -s tests -p "test_*.py" -v
```

### Run a single test file

```bash
python3 -m unittest tests.test_habit -v
python3 -m unittest tests.test_analytics -v
```

### Expected output

```
test_attributes (tests.test_habit.TestHabit) ... ok
test_mark_complete (tests.test_habit.TestHabit) ... ok
test_mark_complete_without_timer (tests.test_habit.TestHabit) ... ok
test_roundtrip (tests.test_habit.TestHabit) ... ok
test_start_records_time (tests.test_habit.TestHabit) ... ok
test_to_dict_has_window_fields (tests.test_habit.TestHabit) ... ok
test_update_habit (tests.test_habit.TestHabit) ... ok
test_upload_proof (tests.test_habit.TestHabit) ... ok
...
----------------------------------------------------------------------
Ran 23 tests in 0.41s

OK
```

### Test files

| File | Module tested | Tests |
|---|---|---|
| `test_habit.py` | `Habit` class | Create, start, complete, proof, update, serialise |
| `test_storage_manager.py` | `StorageManager` | Save, load, overwrite, missing file |
| `test_habit_manager.py` | `HabitManager` | Add, delete, update, start, complete, streak |
| `test_timetable_manager.py` | `TimetableManager` | Sort order, grouping, empty list |
| `test_default_habits.py` | `DefaultHabitManager` | Suggestions, seed data, time simulation |
| `test_reward_manager.py` | `RewardManager` | Assign reward, verify proof |
| `test_congrat_manager.py` | `CongratManager` | Message generation, custom message |
| `test_analytics.py` | `analytics.py` | Streak, rate, filter, rank, report |

---

## 14. Design Principles

### Object-Oriented Programming (OOP)

| Principle | How it is applied |
|---|---|
| Encapsulation | Each class owns its data; external code uses public methods only |
| Single Responsibility | Each module has exactly one job (e.g. `StorageManager` only handles files) |
| Separation of Concerns | Data, logic, storage, and display are fully independent layers |
| Composition | Managers are composed together in `main.py` and `gui_manager.py` |
| Dependency Injection | `HabitManager` receives `StorageManager` as a parameter, making it easy to test with a temporary file |

### Functional Programming (FP) — `analytics/analytics.py`

| Principle | How it is applied |
|---|---|
| Pure functions | Every analytics function returns the same output for the same input |
| No side effects | Analytics functions never modify Habit objects — they only read them |
| `map()` | `update_streaks()` applies streak recalculation to every habit |
| `filter()` | `filter_by_type()`, `filter_by_window()`, `streak_at_risk()` |
| `sorted()` + `lambda` | `weakest_habits()`, `strongest_habits()` rank by completion rate |
| `reduce()` | `generate_report()` aggregates all stats across every habit into one dict |

---

## 15. Known Limitations & Future Work

### Current limitations

- Single user — the app is designed for one user on one device. There is no
  login or multi-user support.
- No cloud sync — data is stored locally in `data/habits.json` only.
- GUI requires Tkinter — if Tkinter is not available, use the CLI (`main.py`).
- Break habits use tick-off, not timer — habits of type `"break"` (e.g.
  "No Junk Food") are marked complete without a Start/Done timer since they
  cover the whole day.

### Planned for Phase 3

- [ ] SQLite database backend (swappable with JSON via `AbstractStorage` interface)
- [ ] Weekly and monthly view in the timetable
- [ ] Export progress report to PDF
- [ ] Notification/reminder system
- [ ] GUI proof image preview in Habit Detail screen
- [ ] Achieve ≥ 85% unit test coverage

---

## Quick Reference

```bash
# Run CLI
python3 main.py

# Run GUI
python3 gui/gui_manager.py

# Run all tests
python3 -m unittest discover -s tests -p "test_*.py" -v

# Back up your data
cp -r data/ data_backup/

# Start fresh (delete all habits)
rm data/habits.json
```
