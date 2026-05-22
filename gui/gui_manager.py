import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import os
import sys

# Add parent folder to path so we can import our project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.habit           import TIME_WINDOWS, get_local_time, format_datetime
from managers.storage_manager   import StorageManager
from managers.habit_manager     import HabitManager
from managers.timetable_manager import TimetableManager
from managers.default_habits    import DefaultHabitManager
from managers.reward_manager    import RewardManager
from managers.congrats_manager   import CongratManager
from analytics.analytics        import (
    generate_report, streak_at_risk, completion_rate, avg_duration,
)


COLORS = {
    "bg":          "#0D3B38",   # deep teal — main background
    "panel":       "#FFFFFF",   # white — card / panel background
    "primary":     "#0D9488",   # teal — buttons, highlights
    "accent":      "#14B8A6",   # mint — accents, active states
    "light_bg":    "#F0FDF9",   # very light mint — alternating rows
    "text_dark":   "#1E293B",   # dark slate — body text
    "text_muted":  "#64748B",   # grey — secondary text
    "success":     "#059669",   # green — complete status
    "warning":     "#D97706",   # amber — in-progress
    "danger":      "#EF4444",   # red — streak at risk
    "border":      "#CCFBF1",   # light mint — borders
    "white":       "#FFFFFF",
    "header_text": "#FFFFFF",   # white text on dark headers
}


def make_button(parent, text, command, style="primary", width=18, pady=6):
    bg_map = {
        "primary": COLORS["primary"],
        "accent":  COLORS["accent"],
        "danger":  COLORS["danger"],
        "muted":   COLORS["text_muted"],
    }
    fg_map = {
        "primary": COLORS["white"],
        "accent":  COLORS["text_dark"],
        "danger":  COLORS["white"],
        "muted":   COLORS["white"],
    }
    bg = bg_map.get(style, COLORS["primary"])
    fg = fg_map.get(style, COLORS["white"])

    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, relief="flat",
        font=("Calibri", 11, "bold"),
        width=width, pady=pady,
        cursor="hand2",
        activebackground=COLORS["accent"],
        activeforeground=COLORS["text_dark"],
    )
    return btn

def make_header(parent, text, size=18):
    return tk.Label(
        parent, text=text,
        bg=COLORS["bg"], fg=COLORS["white"],
        font=("Calibri", size, "bold"),
    )

class HabitTrackerApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Habit Tracker")
        self.geometry("960x680")
        self.resizable(True, True)
        self.configure(bg=COLORS["bg"])
        self.minsize(800, 560)

        os.makedirs("data",    exist_ok=True)
        os.makedirs("uploads", exist_ok=True)

        self.storage  = StorageManager("data/habits.json")
        self.hm       = HabitManager(self.storage)
        self.hm.load()
        self.tm       = TimetableManager(self.hm)
        self.defaults = DefaultHabitManager()
        self.rm       = RewardManager()
        self.cm       = CongratManager()

        settings_path = "data/settings.txt"
        if os.path.exists(settings_path):
            with open(settings_path) as f:
                self.user_tz = f.read().strip() or "UTC"
        else:
            self.user_tz = "UTC"   # will be overwritten by TimezoneScreen

        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.screens = {}
        for ScreenClass in (
            TimezoneScreen,
            MainScreen,
            TimetableScreen,
            AddHabitScreen,
            AnalyticsScreen,
            ManageScreen,
        ):
            screen = ScreenClass(parent=container, app=self)
            self.screens[ScreenClass.__name__] = screen
            screen.grid(row=0, column=0, sticky="nsew")

        self._detail_screen = None

        if not os.path.exists(settings_path):
            self.show_screen("TimezoneScreen")
        else:
            self.show_screen("MainScreen")

    def show_screen(self, name: str):
        screen = self.screens.get(name)
        if screen:
            if hasattr(screen, "refresh"):
                screen.refresh()
            screen.tkraise()

    def show_habit_detail(self, habit_id: int):
        container = list(self.screens.values())[0].master
        if self._detail_screen:
            self._detail_screen.destroy()
        self._detail_screen = HabitDetailScreen(
            parent=container, app=self, habit_id=habit_id
        )
        self._detail_screen.grid(row=0, column=0, sticky="nsew")
        self._detail_screen.tkraise()

    def save_timezone(self, tz: str):
        self.user_tz = tz
        with open("data/settings.txt", "w") as f:
            f.write(tz)

        if not self.hm.get_habits():
            seed = self.defaults.get_four_week_seed(tz)
            for h in seed:
                self.hm.habit_list.append(h)
            self.hm._next_id = len(seed) + 1
            self.hm._persist()

        self.show_screen("MainScreen")

class TimezoneScreen(tk.Frame):
    TIMEZONE_OPTIONS = [
        ("Africa/Lagos",        "WAT  – Nigeria, Ghana, Cameroon"),
        ("Africa/Nairobi",      "EAT  – Kenya, Tanzania, Uganda"),
        ("Africa/Johannesburg", "SAST – South Africa"),
        ("Europe/London",       "GMT/BST – United Kingdom"),
        ("Europe/Berlin",       "CET  – Germany, France, Italy"),
        ("America/New_York",    "EST  – US East Coast"),
        ("America/Los_Angeles", "PST  – US West Coast"),
        ("Asia/Dubai",          "GST  – UAE"),
        ("Asia/Kolkata",        "IST  – India"),
        ("UTC",                 "UTC  – Coordinated Universal Time"),
    ]
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="🗓  Welcome to Habit Tracker",
                 bg=COLORS["bg"], fg=COLORS["white"],
                 font=("Calibri", 22, "bold")).pack(pady=(50, 8))
        tk.Label(self, text="Your timezone is used to record the exact time you\n"
                            "start and finish each habit.",
                 bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Calibri", 12)).pack(pady=(0, 24))

        card = tk.Frame(self, bg=COLORS["panel"], padx=32, pady=24)
        card.pack(padx=60, pady=0, fill="x")

        tk.Label(card, text="Choose your timezone:",
                 bg=COLORS["panel"], fg=COLORS["text_dark"],
                 font=("Calibri", 13, "bold")).pack(anchor="w", pady=(0, 12))

        self._tz_var = tk.StringVar(value=self.TIMEZONE_OPTIONS[0][0])

        for tz_str, label in self.TIMEZONE_OPTIONS:
            row = tk.Frame(card, bg=COLORS["panel"])
            row.pack(fill="x", pady=2)
            tk.Radiobutton(
                row, text=label, variable=self._tz_var, value=tz_str,
                bg=COLORS["panel"], fg=COLORS["text_dark"],
                font=("Calibri", 11),
                activebackground=COLORS["light_bg"],
                selectcolor=COLORS["accent"],
            ).pack(anchor="w")

        tk.Label(card, text="Or type a custom timezone (e.g. America/Chicago):",
                 bg=COLORS["panel"], fg=COLORS["text_muted"],
                 font=("Calibri", 10)).pack(anchor="w", pady=(16, 4))

        self._custom_tz = tk.Entry(card, font=("Calibri", 11), width=30,
                                   bg=COLORS["light_bg"], fg=COLORS["text_dark"],
                                   relief="flat", bd=4)
        self._custom_tz.pack(anchor="w")

        make_button(card, "Confirm & Continue →",
                    command=self._confirm, width=24, pady=8).pack(pady=(20, 0))

    def _confirm(self):
        custom = self._custom_tz.get().strip()
        tz = custom if custom else self._tz_var.get()
        self.app.save_timezone(tz)


class MainScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=COLORS["bg"])
        top.pack(fill="x", padx=40, pady=(30, 0))

        self._time_label = tk.Label(top, text="",
                                    bg=COLORS["bg"], fg=COLORS["accent"],
                                    font=("Calibri", 12))
        self._time_label.pack(side="right")

        make_header(top, "🗓  Habit Tracker", size=22).pack(side="left")

        self._progress_card = tk.Frame(self, bg=COLORS["panel"],
                                       padx=24, pady=16)
        self._progress_card.pack(padx=40, pady=(20, 0), fill="x")

        self._progress_label = tk.Label(self._progress_card, text="",
                                        bg=COLORS["panel"], fg=COLORS["text_dark"],
                                        font=("Calibri", 14, "bold"))
        self._progress_label.pack(anchor="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Teal.Horizontal.TProgressbar",
                         troughcolor=COLORS["border"],
                         background=COLORS["primary"],
                         thickness=14)
        self._pbar = ttk.Progressbar(self._progress_card, length=400,
                                     style="Teal.Horizontal.TProgressbar")
        self._pbar.pack(anchor="w", pady=(8, 0))

        self._streak_alert = tk.Label(self._progress_card, text="",
                                      bg=COLORS["panel"], fg=COLORS["danger"],
                                      font=("Calibri", 11, "bold"),
                                      wraplength=700, justify="left")
        self._streak_alert.pack(anchor="w", pady=(6, 0))

        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(padx=40, pady=24, fill="x")

        buttons = [
            ("📋  View Timetable",    "TimetableScreen", "primary"),
            ("➕  Add New Habit",      "AddHabitScreen",  "primary"),
            ("📊  Analytics",          "AnalyticsScreen", "primary"),
            ("⚙️  Manage Habits",      "ManageScreen",    "muted"),
        ]

        for label, screen, style in buttons:
            make_button(nav, label,
                        command=lambda s=screen: self.app.show_screen(s),
                        style=style, width=22, pady=10
                        ).pack(side="left", padx=8)

        tk.Label(self, text="Today's Habits",
                 bg=COLORS["bg"], fg=COLORS["white"],
                 font=("Calibri", 14, "bold")).pack(anchor="w", padx=40, pady=(8, 4))

        self._habits_frame = tk.Frame(self, bg=COLORS["bg"])
        self._habits_frame.pack(padx=40, fill="both", expand=True)

        self._update_clock()

    def refresh(self):
        habits = self.app.hm.get_habits()
        done  = sum(1 for h in habits if h.status == "complete")
        total = len(habits)

        self._progress_label.config(
            text=f"Today's progress: {done} / {total} habits complete"
        )
        self._pbar["maximum"] = max(total, 1)
        self._pbar["value"]   = done

        at_risk = streak_at_risk(habits)
        if at_risk:
            names = ", ".join(h.habit_name for h in at_risk)
            self._streak_alert.config(
                text=f"⚠  Streak alert! Do these today: {names}"
            )
        else:
            self._streak_alert.config(text="")

        for widget in self._habits_frame.winfo_children():
            widget.destroy()

        for habit in habits[:8]:   # show up to 8 characters on dashboard
            self._make_habit_row(habit)

    def _make_habit_row(self, habit):
        row = tk.Frame(self._habits_frame, bg=COLORS["panel"], pady=6, padx=12)
        row.pack(fill="x", pady=3)

        dot_color = COLORS["success"] if habit.status == "complete" \
                    else (COLORS["warning"] if habit.actual_start_time
                          else COLORS["text_muted"])
        tk.Label(row, text="●", bg=COLORS["panel"], fg=dot_color,
                 font=("Calibri", 14)).pack(side="left", padx=(0, 10))

        tk.Label(row, text=habit.habit_name,
                 bg=COLORS["panel"], fg=COLORS["text_dark"],
                 font=("Calibri", 12, "bold"), width=22, anchor="w").pack(side="left")

        tk.Label(row, text=f"{habit.preferred_window}  ({habit.scheduled_start}–{habit.scheduled_end})",
                 bg=COLORS["panel"], fg=COLORS["text_muted"],
                 font=("Calibri", 10)).pack(side="left", padx=(8, 0))

        if habit.current_streak > 0:
            tk.Label(row, text=f"🔥 {habit.current_streak}",
                     bg=COLORS["panel"], fg=COLORS["warning"],
                     font=("Calibri", 10, "bold")).pack(side="right", padx=8)

        make_button(row, "Details",
                    command=lambda hid=habit.habit_id: self.app.show_habit_detail(hid),
                    style="accent", width=8, pady=2).pack(side="right", padx=4)

    def _update_clock(self):
        now = get_local_time(self.app.user_tz)
        self._time_label.config(text=format_datetime(now))
        self.after(1000, self._update_clock)   # schedule next update in 1 second


class TimetableScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(24, 0))

        make_header(header, "📋  Today's Timetable").pack(side="left")
        make_button(header, "← Back",
                    command=lambda: self.app.show_screen("MainScreen"),
                    style="muted", width=10, pady=4).pack(side="right")

        self._time_label = tk.Label(header, text="",
                                    bg=COLORS["bg"], fg=COLORS["accent"],
                                    font=("Calibri", 11))
        self._time_label.pack(side="right", padx=16)

        cols_frame = tk.Frame(self, bg=COLORS["primary"])
        cols_frame.pack(fill="x", padx=30, pady=(16, 0))

        headers = [
            ("Window",    180),
            ("Habit",     200),
            ("Type",       80),
            ("Status",    130),
            ("Actual Time",180),
            ("Actions",   200),
        ]
        for col_name, col_w in headers:
            tk.Label(cols_frame, text=col_name,
                     bg=COLORS["primary"], fg=COLORS["white"],
                     font=("Calibri", 11, "bold"),
                     width=col_w // 8, anchor="w", padx=8, pady=6
                     ).pack(side="left")

        scroll_container = tk.Frame(self, bg=COLORS["bg"])
        scroll_container.pack(fill="both", expand=True, padx=30, pady=(0, 16))

        canvas = tk.Canvas(scroll_container, bg=COLORS["bg"],
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical",
                                  command=canvas.yview)
        self._rows_frame = tk.Frame(canvas, bg=COLORS["bg"])

        self._rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._update_clock()

    def refresh(self):
        for widget in self._rows_frame.winfo_children():
            widget.destroy()

        timetable = self.app.tm.get_timetable()

        if not timetable:
            tk.Label(self._rows_frame,
                     text="No habits yet. Use 'Add New Habit' to get started!",
                     bg=COLORS["bg"], fg=COLORS["accent"],
                     font=("Calibri", 13)).pack(pady=40)
            return

        for i, row_habits in enumerate(timetable):
            for habit in row_habits:
                bg = COLORS["light_bg"] if i % 2 == 0 else COLORS["panel"]
                self._make_row(habit, bg)

    def _make_row(self, habit, bg):
        row = tk.Frame(self._rows_frame, bg=bg, pady=6, padx=8)
        row.pack(fill="x")

        tk.Label(row, text=f"{habit.preferred_window}\n{habit.scheduled_start}–{habit.scheduled_end}",
                 bg=bg, fg=COLORS["text_dark"],
                 font=("Calibri", 10), width=22, anchor="w", justify="left"
                 ).pack(side="left")

        name_frame = tk.Frame(row, bg=bg)
        name_frame.pack(side="left", padx=4)
        tk.Label(name_frame, text=habit.habit_name,
                 bg=bg, fg=COLORS["text_dark"],
                 font=("Calibri", 11, "bold"), width=22, anchor="w"
                 ).pack(anchor="w")
        if habit.current_streak > 0:
            tk.Label(name_frame, text=f"🔥 {habit.current_streak}-day streak",
                     bg=bg, fg=COLORS["warning"],
                     font=("Calibri", 9)).pack(anchor="w")

        type_color = COLORS["primary"] if habit.habit_type == "build" \
                     else COLORS["danger"]
        tk.Label(row, text=habit.habit_type,
                 bg=type_color, fg=COLORS["white"],
                 font=("Calibri", 9, "bold"),
                 padx=6, pady=2).pack(side="left", padx=6)

        if habit.status == "complete":
            status_text  = "✓ complete"
            status_color = COLORS["success"]
        elif habit.actual_start_time:
            status_text  = "▶ in progress"
            status_color = COLORS["warning"]
        else:
            status_text  = "○ pending"
            status_color = COLORS["text_muted"]

        tk.Label(row, text=status_text,
                 bg=bg, fg=status_color,
                 font=("Calibri", 10, "bold"), width=14, anchor="w"
                 ).pack(side="left")

        time_frame = tk.Frame(row, bg=bg)
        time_frame.pack(side="left", padx=6)
        if habit.actual_start_time:
            tk.Label(time_frame, text=f"▶ {habit.actual_start_time}",
                     bg=bg, fg=COLORS["text_muted"],
                     font=("Calibri", 9)).pack(anchor="w")
        if habit.actual_end_time:
            tk.Label(time_frame, text=f"■ {habit.actual_end_time}",
                     bg=bg, fg=COLORS["text_muted"],
                     font=("Calibri", 9)).pack(anchor="w")
            if habit.completion_history:
                dur = habit.completion_history[-1].get("duration_mins")
                if dur is not None:
                    tk.Label(time_frame, text=f"⏱ {dur} min",
                             bg=bg, fg=COLORS["primary"],
                             font=("Calibri", 9, "bold")).pack(anchor="w")

        btn_frame = tk.Frame(row, bg=bg)
        btn_frame.pack(side="right", padx=4)

        if habit.status != "complete":
            if not habit.actual_start_time:
                make_button(btn_frame, "▶ Start",
                            command=lambda hid=habit.habit_id: self._start(hid),
                            style="primary", width=8, pady=2).pack(side="left", padx=2)
            else:
                make_button(btn_frame, "✓ Done",
                            command=lambda hid=habit.habit_id: self._done(hid),
                            style="accent", width=8, pady=2).pack(side="left", padx=2)

        make_button(btn_frame, "Details",
                    command=lambda hid=habit.habit_id: self.app.show_habit_detail(hid),
                    style="muted", width=8, pady=2).pack(side="left", padx=2)

    def _start(self, habit_id: int):
        recorded = self.app.hm.start_habit(habit_id)
        messagebox.showinfo("Started!",
                            f"Started at {recorded}\nPress Done when you finish.")
        self.refresh()

    def _done(self, habit_id: int):
        dialog = _NotesDialog(self, title="Mark Complete")
        self.wait_window(dialog)

        notes = dialog.result if dialog.result is not None else ""
        habit = self.app.hm.get_habit_by_id(habit_id)
        use_timer = bool(habit and habit.actual_start_time)
        self.app.hm.mark_complete(habit_id, notes, use_timer)

        habit = self.app.hm.get_habit_by_id(habit_id)
        msg = self.app.cm.get_custom_message(habit)
        messagebox.showinfo("Well done! 🎉", msg)
        self.refresh()

    def _update_clock(self):
        now = get_local_time(self.app.user_tz)
        self._time_label.config(text=format_datetime(now))
        self.after(1000, self._update_clock)


class AddHabitScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(24, 0))
        make_header(header, "➕  Add New Habit").pack(side="left")
        make_button(header, "← Back",
                    command=lambda: self.app.show_screen("MainScreen"),
                    style="muted", width=10, pady=4).pack(side="right")

        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        form_outer = tk.Frame(canvas, bg=COLORS["bg"])
        form_outer.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form_outer, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=16)
        scrollbar.pack(side="right", fill="y")

        card = tk.Frame(form_outer, bg=COLORS["panel"], padx=32, pady=24)
        card.pack(fill="x", pady=8)

        def field(label, row_num):
            tk.Label(card, text=label,
                     bg=COLORS["panel"], fg=COLORS["text_dark"],
                     font=("Calibri", 11, "bold")).grid(
                         row=row_num, column=0, sticky="w", pady=6, padx=(0, 16))

        field("Habit Name:", 0)
        self._name_var = tk.StringVar()
        tk.Entry(card, textvariable=self._name_var,
                 font=("Calibri", 11), width=32,
                 bg=COLORS["light_bg"], fg=COLORS["text_dark"],
                 relief="flat", bd=4).grid(row=0, column=1, sticky="w", pady=6)

        field("Habit Type:", 1)
        self._type_var = tk.StringVar(value="build")
        type_frame = tk.Frame(card, bg=COLORS["panel"])
        type_frame.grid(row=1, column=1, sticky="w", pady=6)
        for val, label in [("build", "Build  (do it more)"),
                            ("break", "Break  (do it less)")]:
            tk.Radiobutton(type_frame, text=label, variable=self._type_var,
                           value=val, bg=COLORS["panel"], fg=COLORS["text_dark"],
                           font=("Calibri", 11),
                           selectcolor=COLORS["accent"]).pack(anchor="w")

        field("Time Window:", 2)
        self._window_var = tk.StringVar()
        window_labels = [f"{lbl}  ({start}–{end})"
                         for lbl, start, end in TIME_WINDOWS]
        self._window_var.set(window_labels[1])   # default to "Morning"
        window_menu = ttk.Combobox(card, textvariable=self._window_var,
                                   values=window_labels,
                                   state="readonly", width=30,
                                   font=("Calibri", 11))
        window_menu.grid(row=2, column=1, sticky="w", pady=6)

        tk.Label(card, text="↑ Your actual start & end times will be\n"
                            "  recorded automatically when you press Start / Done.",
                 bg=COLORS["panel"], fg=COLORS["text_muted"],
                 font=("Calibri", 9), justify="left").grid(
                     row=3, column=1, sticky="w", pady=(0, 6))

        field("Frequency:", 4)
        self._freq_var = tk.StringVar(value="daily")
        freq_frame = tk.Frame(card, bg=COLORS["panel"])
        freq_frame.grid(row=4, column=1, sticky="w", pady=6)
        for val in ("daily", "weekly", "monthly"):
            tk.Radiobutton(freq_frame, text=val.capitalize(),
                           variable=self._freq_var, value=val,
                           bg=COLORS["panel"], fg=COLORS["text_dark"],
                           font=("Calibri", 11),
                           selectcolor=COLORS["accent"]).pack(side="left", padx=8)

        field("Reward:", 5)
        self._reward_var = tk.StringVar()
        tk.Entry(card, textvariable=self._reward_var,
                 font=("Calibri", 11), width=32,
                 bg=COLORS["light_bg"], fg=COLORS["text_dark"],
                 relief="flat", bd=4).grid(row=5, column=1, sticky="w", pady=6)

        field("Motivational\nMessage:", 6)
        self._msg_var = tk.StringVar()
        tk.Entry(card, textvariable=self._msg_var,
                 font=("Calibri", 11), width=32,
                 bg=COLORS["light_bg"], fg=COLORS["text_dark"],
                 relief="flat", bd=4).grid(row=6, column=1, sticky="w", pady=6)

        tk.Label(card, text="— or browse suggestions —",
                 bg=COLORS["panel"], fg=COLORS["text_muted"],
                 font=("Calibri", 10)).grid(row=7, column=0, columnspan=2, pady=12)

        suggestions = self.app.defaults.get_suggestions()
        self._suggestion_var = tk.StringVar()
        suggestion_labels = [f"{n}  ({ht}, {win}, {freq})"
                             for n, ht, win, freq, _ in suggestions]
        ttk.Combobox(card, textvariable=self._suggestion_var,
                     values=suggestion_labels,
                     state="readonly", width=42,
                     font=("Calibri", 10)).grid(
                         row=8, column=0, columnspan=2, sticky="w", pady=4)

        make_button(card, "Load Suggestion →",
                    command=lambda: self._load_suggestion(suggestions),
                    style="accent", width=20, pady=4).grid(
                        row=9, column=0, columnspan=2, sticky="w", pady=(4, 16))

        self._status_label = tk.Label(card, text="",
                                      bg=COLORS["panel"], fg=COLORS["success"],
                                      font=("Calibri", 11))
        self._status_label.grid(row=10, column=0, columnspan=2, pady=4)

        make_button(card, "✓  Save Habit",
                    command=self._save, style="primary",
                    width=20, pady=8).grid(row=11, column=0, columnspan=2)

    def _load_suggestion(self, suggestions):
        label = self._suggestion_var.get()
        if not label:
            return
        for name, htype, window_label, freq, reward in suggestions:
            if label.startswith(name):
                self._name_var.set(name)
                self._type_var.set(htype)
                self._freq_var.set(freq)
                self._reward_var.set(reward)
                for i, (lbl, start, end) in enumerate(TIME_WINDOWS):
                    if lbl == window_label:
                        win_str = f"{lbl}  ({start}–{end})"
                        self._window_var.set(win_str)
                        break
                break

    def _save(self):
        name   = self._name_var.get().strip()
        htype  = self._type_var.get()
        freq   = self._freq_var.get()
        reward = self._reward_var.get().strip()
        msg    = self._msg_var.get().strip()

        if not name:
            self._status_label.config(text="⚠  Habit name is required.",
                                      fg=COLORS["danger"])
            return

        selected_win = self._window_var.get()
        window_index = 1   # default to Morning
        for i, (lbl, start, end) in enumerate(TIME_WINDOWS):
            if selected_win.startswith(lbl):
                window_index = i
                break

        self.app.hm.add_habit(name, htype, window_index, freq,
                               reward or "Well done!", self.app.user_tz, msg)

        self._status_label.config(text=f"✓  '{name}' saved!", fg=COLORS["success"])

        # Clear form
        self._name_var.set("")
        self._reward_var.set("")
        self._msg_var.set("")

    def refresh(self):
        pass   # nothing to reload on this screen



class HabitDetailScreen(tk.Frame):
    def __init__(self, parent, app, habit_id: int):
        super().__init__(parent, bg=COLORS["bg"])
        self.app      = app
        self.habit_id = habit_id
        self._build()

    def _build(self):
        habit = self.app.hm.get_habit_by_id(self.habit_id)
        if not habit:
            tk.Label(self, text="Habit not found.",
                     bg=COLORS["bg"], fg=COLORS["white"],
                     font=("Calibri", 14)).pack(pady=40)
            return

        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(24, 0))
        make_header(header, f"🔍  {habit.habit_name}").pack(side="left")
        make_button(header, "← Back",
                    command=lambda: self.app.show_screen("MainScreen"),
                    style="muted", width=10, pady=4).pack(side="right")

        card = tk.Frame(self, bg=COLORS["panel"], padx=24, pady=16)
        card.pack(padx=30, pady=16, fill="x")

        stats = [
            ("Type",         habit.habit_type.capitalize()),
            ("Window",       f"{habit.preferred_window}  ({habit.scheduled_start}–{habit.scheduled_end})"),
            ("Frequency",    habit.frequency.capitalize()),
            ("Reward",       habit.reward),
            ("Status",       habit.status.capitalize()),
            ("Current Streak",f"🔥 {habit.current_streak} days"),
            ("Longest Streak",f"🏆 {habit.longest_streak} days"),
            ("Completion Rate",f"{completion_rate(habit)*100:.1f}%"),
        ]
        if avg_duration(habit) is not None:
            stats.append(("Avg Duration", f"⏱ {avg_duration(habit)} min"))
        if habit.actual_start_time:
            stats.append(("Started Today", habit.actual_start_time))
        if habit.actual_end_time:
            stats.append(("Finished Today", habit.actual_end_time))

        for i, (label, value) in enumerate(stats):
            tk.Label(card, text=f"{label}:",
                     bg=COLORS["panel"], fg=COLORS["text_muted"],
                     font=("Calibri", 10, "bold"), width=16, anchor="e"
                     ).grid(row=i, column=0, sticky="e", padx=(0, 8), pady=3)
            tk.Label(card, text=value,
                     bg=COLORS["panel"], fg=COLORS["text_dark"],
                     font=("Calibri", 11), anchor="w"
                     ).grid(row=i, column=1, sticky="w", pady=3)

        btn_row = tk.Frame(self, bg=COLORS["bg"])
        btn_row.pack(padx=30, pady=8, fill="x")

        if habit.status != "complete":
            if not habit.actual_start_time:
                make_button(btn_row, "▶  Start Habit",
                            command=self._start,
                            style="primary", width=16, pady=6).pack(side="left", padx=6)
            else:
                make_button(btn_row, "✓  Mark Done",
                            command=self._done,
                            style="accent", width=16, pady=6).pack(side="left", padx=6)

        make_button(btn_row, "📎  Upload Proof",
                    command=self._upload_proof,
                    style="muted", width=16, pady=6).pack(side="left", padx=6)

        tk.Label(self, text="Recent History (last 7 entries)",
                 bg=COLORS["bg"], fg=COLORS["white"],
                 font=("Calibri", 12, "bold")).pack(anchor="w", padx=30, pady=(12, 4))

        cols = tk.Frame(self, bg=COLORS["primary"])
        cols.pack(fill="x", padx=30)
        for col, w in [("Date", 12), ("Start", 12), ("End", 12),
                       ("Duration", 10), ("Status", 10), ("Notes", 24)]:
            tk.Label(cols, text=col, bg=COLORS["primary"], fg=COLORS["white"],
                     font=("Calibri", 10, "bold"), width=w, anchor="w",
                     padx=6, pady=4).pack(side="left")

        history_frame = tk.Frame(self, bg=COLORS["bg"])
        history_frame.pack(fill="x", padx=30)

        recent = list(reversed(habit.completion_history))[:7]
        for i, entry in enumerate(recent):
            bg = COLORS["light_bg"] if i % 2 == 0 else COLORS["panel"]
            erow = tk.Frame(history_frame, bg=bg)
            erow.pack(fill="x")
            done = entry.get("completed", False)
            for val, w in [
                (entry.get("date", ""), 12),
                (entry.get("actual_start") or "—", 12),
                (entry.get("actual_end")   or "—", 12),
                (f"{entry.get('duration_mins')} min" if entry.get("duration_mins") is not None else "—", 10),
                ("✓" if done else "✗", 10),
                (entry.get("notes", "")[:30], 24),
            ]:
                tk.Label(erow, text=val, bg=bg,
                         fg=COLORS["success"] if val == "✓" else
                            COLORS["danger"] if val == "✗" else COLORS["text_dark"],
                         font=("Calibri", 10), width=w, anchor="w",
                         padx=6, pady=4).pack(side="left")

    def _start(self):
        recorded = self.app.hm.start_habit(self.habit_id)
        messagebox.showinfo("Started!", f"Started at {recorded}")
        self.app.show_habit_detail(self.habit_id)   # rebuild with new data

    def _done(self):
        dialog = _NotesDialog(self, title="Mark Complete")
        self.wait_window(dialog)
        notes = dialog.result if dialog.result is not None else ""
        habit = self.app.hm.get_habit_by_id(self.habit_id)
        use_timer = bool(habit and habit.actual_start_time)
        self.app.hm.mark_complete(self.habit_id, notes, use_timer)
        habit = self.app.hm.get_habit_by_id(self.habit_id)
        messagebox.showinfo("Well done! 🎉", self.app.cm.get_custom_message(habit))
        self.app.show_habit_detail(self.habit_id)

    def _upload_proof(self):
        path = filedialog.askopenfilename(
            title="Select proof image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                       ("All files", "*.*")]
        )
        if path:
            if self.app.rm.verify_proof(path):
                self.app.hm.get_habit_by_id(self.habit_id).upload_proof(path)
                self.app.hm._persist()
                messagebox.showinfo("Proof saved!", f"Image saved:\n{path}")
                self.app.show_habit_detail(self.habit_id)
            else:
                messagebox.showerror("Invalid file",
                                     "Please select a valid image file.")

    def refresh(self):
        pass

class AnalyticsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build_shell()

    def _build_shell(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(24, 0))
        make_header(header, "📊  Analytics & Progress").pack(side="left")
        make_button(header, "← Back",
                    command=lambda: self.app.show_screen("MainScreen"),
                    style="muted", width=10, pady=4).pack(side="right")

        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._content = tk.Frame(canvas, bg=COLORS["bg"])
        self._content.bind("<Configure>",
                           lambda e: canvas.configure(
                               scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=16)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        for w in self._content.winfo_children():
            w.destroy()

        habits = self.app.hm.get_habits()
        if not habits:
            tk.Label(self._content, text="No habits yet.",
                     bg=COLORS["bg"], fg=COLORS["accent"],
                     font=("Calibri", 13)).pack(pady=40)
            return

        report = generate_report(habits)

        card = tk.Frame(self._content, bg=COLORS["panel"], padx=24, pady=16)
        card.pack(fill="x", pady=(8, 16))
        tk.Label(card, text="Summary",
                 bg=COLORS["panel"], fg=COLORS["text_dark"],
                 font=("Calibri", 13, "bold")).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        summary_rows = [
            ("Total habits",         str(report["total_habits"])),
            ("Build habits",         str(report["build_habits"])),
            ("Break habits",         str(report["break_habits"])),
            ("Avg completion rate",  f"{report['avg_completion_rate']*100:.1f}%"),
            ("Longest streak ever",  f"🔥 {report['longest_overall_streak']} days"),
            ("Most consistent",      report["most_consistent"]),
            ("Needs improvement",    report["needs_improvement"]),
        ]
        if report["avg_duration_mins"] is not None:
            summary_rows.append(("Avg actual duration",
                                  f"⏱ {report['avg_duration_mins']} min"))

        for i, (lbl, val) in enumerate(summary_rows, start=1):
            tk.Label(card, text=lbl + ":",
                     bg=COLORS["panel"], fg=COLORS["text_muted"],
                     font=("Calibri", 10, "bold"), width=22, anchor="e"
                     ).grid(row=i, column=0, sticky="e", padx=(0, 8), pady=2)
            tk.Label(card, text=val,
                     bg=COLORS["panel"], fg=COLORS["text_dark"],
                     font=("Calibri", 11), anchor="w"
                     ).grid(row=i, column=1, sticky="w", pady=2)

        at_risk = streak_at_risk(habits)
        if at_risk:
            alert_card = tk.Frame(self._content, bg="#FEF2F2", padx=16, pady=12)
            alert_card.pack(fill="x", pady=(0, 12))
            tk.Label(alert_card, text="⚠  Streaks at risk today!",
                     bg="#FEF2F2", fg=COLORS["danger"],
                     font=("Calibri", 12, "bold")).pack(anchor="w")
            for h in at_risk:
                tk.Label(alert_card,
                         text=f"  •  {h.habit_name} — {h.current_streak}-day streak",
                         bg="#FEF2F2", fg=COLORS["danger"],
                         font=("Calibri", 11)).pack(anchor="w")

        tk.Label(self._content, text="Per-Habit Breakdown",
                 bg=COLORS["bg"], fg=COLORS["white"],
                 font=("Calibri", 13, "bold")).pack(anchor="w", pady=(8, 4))

        col_hdr = tk.Frame(self._content, bg=COLORS["primary"])
        col_hdr.pack(fill="x")
        for col, w in [("Habit", 22), ("Rate", 8), ("Streak", 8),
                       ("Longest", 8), ("Avg Duration", 12)]:
            tk.Label(col_hdr, text=col, bg=COLORS["primary"], fg=COLORS["white"],
                     font=("Calibri", 10, "bold"), width=w, anchor="w",
                     padx=6, pady=4).pack(side="left")

        for i, h in enumerate(habits):
            bg = COLORS["light_bg"] if i % 2 == 0 else COLORS["panel"]
            row = tk.Frame(self._content, bg=bg)
            row.pack(fill="x")
            rate = completion_rate(h)
            dur  = avg_duration(h)
            for val, w in [
                (h.habit_name, 22),
                (f"{rate*100:.1f}%", 8),
                (f"🔥 {h.current_streak}", 8),
                (f"🏆 {h.longest_streak}", 8),
                (f"{dur} min" if dur else "—", 12),
            ]:
                tk.Label(row, text=val, bg=bg, fg=COLORS["text_dark"],
                         font=("Calibri", 10), width=w, anchor="w",
                         padx=6, pady=4).pack(side="left")


class ManageScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build_shell()

    def _build_shell(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(24, 0))
        make_header(header, "⚙️  Manage Habits").pack(side="left")
        make_button(header, "← Back",
                    command=lambda: self.app.show_screen("MainScreen"),
                    style="muted", width=10, pady=4).pack(side="right")

        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._list_frame = tk.Frame(canvas, bg=COLORS["bg"])
        self._list_frame.bind("<Configure>",
                              lambda e: canvas.configure(
                                  scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=16)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        habits = self.app.hm.get_habits()
        if not habits:
            tk.Label(self._list_frame, text="No habits yet.",
                     bg=COLORS["bg"], fg=COLORS["accent"],
                     font=("Calibri", 13)).pack(pady=40)
            return

        for i, habit in enumerate(habits):
            bg = COLORS["light_bg"] if i % 2 == 0 else COLORS["panel"]
            row = tk.Frame(self._list_frame, bg=bg, pady=8, padx=12)
            row.pack(fill="x", pady=2)

            # Habit info
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=habit.habit_name,
                     bg=bg, fg=COLORS["text_dark"],
                     font=("Calibri", 12, "bold")).pack(anchor="w")
            tk.Label(info,
                     text=f"{habit.preferred_window} · {habit.habit_type} · "
                          f"{habit.frequency} · streak {habit.current_streak}",
                     bg=bg, fg=COLORS["text_muted"],
                     font=("Calibri", 10)).pack(anchor="w")

            # Edit / Delete buttons
            btns = tk.Frame(row, bg=bg)
            btns.pack(side="right")
            make_button(btns, "Edit",
                        command=lambda h=habit: self._edit(h),
                        style="primary", width=8, pady=3).pack(side="left", padx=4)
            make_button(btns, "Delete",
                        command=lambda hid=habit.habit_id: self._delete(hid),
                        style="danger", width=8, pady=3).pack(side="left", padx=4)

    def _edit(self, habit):
        dialog = _EditHabitDialog(self, app=self.app, habit=habit)
        self.wait_window(dialog)
        self.refresh()

    def _delete(self, habit_id: int):
        habit = self.app.hm.get_habit_by_id(habit_id)
        if messagebox.askyesno("Delete habit",
                               f"Delete '{habit.habit_name}'? This cannot be undone."):
            self.app.hm.delete_habit(habit_id)
            self.refresh()

class _NotesDialog(tk.Toplevel):
    def __init__(self, parent, title="Add Note"):
        super().__init__(parent)
        self.title(title)
        self.geometry("380x180")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)
        self.result = None
        self._build()

    def _build(self):
        tk.Label(self, text="Add a note (optional):",
                 bg=COLORS["bg"], fg=COLORS["white"],
                 font=("Calibri", 11)).pack(pady=(20, 6))
        self._entry = tk.Entry(self, font=("Calibri", 11), width=36,
                               bg=COLORS["light_bg"], fg=COLORS["text_dark"],
                               relief="flat", bd=4)
        self._entry.pack(pady=4)
        self._entry.focus()
        btn_row = tk.Frame(self, bg=COLORS["bg"])
        btn_row.pack(pady=12)
        make_button(btn_row, "OK", command=self._ok,
                    style="primary", width=10, pady=4).pack(side="left", padx=6)
        make_button(btn_row, "Skip", command=self._skip,
                    style="muted", width=10, pady=4).pack(side="left", padx=6)
        self.bind("<Return>", lambda e: self._ok())

    def _ok(self):
        self.result = self._entry.get().strip()
        self.destroy()

    def _skip(self):
        self.result = ""
        self.destroy()

class _EditHabitDialog(tk.Toplevel):
    def __init__(self, parent, app, habit):
        super().__init__(parent)
        self.title(f"Edit: {habit.habit_name}")
        self.geometry("460x420")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)
        self.app   = app
        self.habit = habit
        self._build()

    def _build(self):
        card = tk.Frame(self, bg=COLORS["panel"], padx=24, pady=20)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        def row(label, row_num, widget):
            tk.Label(card, text=label,
                     bg=COLORS["panel"], fg=COLORS["text_dark"],
                     font=("Calibri", 10, "bold"), width=14, anchor="e"
                     ).grid(row=row_num, column=0, sticky="e", padx=(0,8), pady=5)
            widget.grid(row=row_num, column=1, sticky="w", pady=5)

        self._name = tk.StringVar(value=self.habit.habit_name)
        row("Name:", 0, tk.Entry(card, textvariable=self._name,
                                  font=("Calibri", 11), width=26,
                                  bg=COLORS["light_bg"], relief="flat", bd=3))

        self._reward = tk.StringVar(value=self.habit.reward)
        row("Reward:", 1, tk.Entry(card, textvariable=self._reward,
                                    font=("Calibri", 11), width=26,
                                    bg=COLORS["light_bg"], relief="flat", bd=3))

        self._msg = tk.StringVar(value=self.habit.custom_message)
        row("Message:", 2, tk.Entry(card, textvariable=self._msg,
                                     font=("Calibri", 11), width=26,
                                     bg=COLORS["light_bg"], relief="flat", bd=3))

        self._win_var = tk.StringVar()
        window_labels = [f"{lbl}  ({s}–{e})" for lbl, s, e in TIME_WINDOWS]
        current = f"{self.habit.preferred_window}  ({self.habit.scheduled_start}–{self.habit.scheduled_end})"
        self._win_var.set(current if current in window_labels else window_labels[1])

        win_combo = ttk.Combobox(card, textvariable=self._win_var,
                                  values=window_labels, state="readonly",
                                  width=26, font=("Calibri", 10))
        row("Window:", 3, win_combo)

        self._status = tk.Label(card, text="", bg=COLORS["panel"],
                                 fg=COLORS["success"], font=("Calibri", 10))
        self._status.grid(row=4, column=0, columnspan=2, pady=4)

        make_button(card, "Save Changes", command=self._save,
                    style="primary", width=18, pady=6
                    ).grid(row=5, column=0, columnspan=2, pady=(8, 0))

    def _save(self):
        sel = self._win_var.get()
        window_index = 1
        for i, (lbl, s, e) in enumerate(TIME_WINDOWS):
            if sel.startswith(lbl):
                window_index = i
                break

        self.app.hm.update_habit(
            self.habit.habit_id,
            habit_name=self._name.get().strip(),
            reward=self._reward.get().strip(),
            custom_message=self._msg.get().strip(),
            window_index=window_index,
        )
        self._status.config(text="✓ Saved!")
        self.after(800, self.destroy)

if __name__ == "__main__":
    app = HabitTrackerApp()
    app.mainloop()
