# Timetable-Based Habit Tracking Application

A Python habit tracker that organises habits into a timetable by time window. Users choose a time window (e.g. Morning, Evening) instead of typing exact times — the app automatically records the real clock time when a habit is started and finished.

---

## Requirements

- Python 3.9 or higher
- No external packages needed (standard library only)
- Tkinter (included with Python) — only needed for the GUI

Check your Python version:
```bash
python --version
```

---

## How to Run

**1. Download the project and open a terminal in the project folder:**
```bash
cd habit_tracker
```

**2. Run the CLI:**
```bash
python main.py
```

**Or run the GUI:**
```bash
python gui/gui_manager.py
```

> On Windows, if `python` doesn't work, try `py` instead.

**3. First launch:** the app will ask you to choose your timezone (one-time setup), then offer to load sample data — 5 predefined habits with 4 weeks of history.

---

## Using the App

| Action | CLI | GUI |
|---|---|---|
| Add a habit | `[4] Add a new habit` | "Add New Habit" button |
| Start a habit | `[2] Start a habit` | "▶ Start" button |
| Mark a habit done | `[3] Mark habit done` | "✓ Done" button |
| View your timetable | `[1] View timetable` | "View Timetable" button |
| See analytics | `[6] Analytics` | "Analytics" button |
| Delete a habit | `[5] Delete a habit` | "Manage Habits" → Delete |

---

## Running the Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## Project Structure

```
habit_tracker/
├── main.py                # Run this for the CLI
├── cli.py                 # CLI logic
├── models/habit.py        # Habit class
├── managers/               # CRUD, storage, timetable, rewards, messages
├── analytics/analytics.py # Functional programming analytics
├── gui/gui_manager.py     # Tkinter GUI
├── tests/                  # Unit tests
└── data/                    # Auto-created — stores your habit data
```

---