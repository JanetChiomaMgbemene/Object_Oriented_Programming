class TimetableManager:
    def __init__(self, habit_manager):
        self._hm = habit_manager
        self.timetable_structure: list = []

    def organise_habits(self) -> None:
        habits = self._hm.get_habits()
        if not habits:
            self.timetable_structure = []
            return

        sorted_habits = sorted(habits, key=lambda h: h.scheduled_start)

        groups: dict = {}         # Group by preferred_window label
        for habit in sorted_habits:
            key = f"{habit.scheduled_start}|{habit.preferred_window}"
            if key not in groups:
                groups[key] = []
            groups[key].append(habit)

        self.timetable_structure = list(groups.values())

    def get_timetable(self) -> list:
        self.organise_habits()
        return self.timetable_structure

    def get_slot(self, window_label: str) -> list:
        return [h for h in self._hm.get_habits()
                if h.preferred_window == window_label]

    def display_timetable(self) -> str:
        self.organise_habits()

        if not self.timetable_structure:
            return "\n  No habits yet. Add a habit to get started!\n"

        col_w  = 20   # window column
        col_n  = 22   # name column
        col_t  = 7    # type column
        col_s  = 14   # status column
        total  = col_w + col_n + col_t + col_s + 5

        sep_row  = "├" + "─"*col_w + "┼" + "─"*col_n + "┼" + "─"*col_t + "┼" + "─"*col_s + "┤"
        top_row  = "┌" + "─"*total + "┐"
        bot_row  = "└" + "─"*col_w + "┴" + "─"*col_n + "┴" + "─"*col_t + "┴" + "─"*col_s + "┘"

        lines = []
        lines.append(top_row)
        lines.append("│" + " HABIT TIMETABLE".center(total) + "│")
        lines.append("├" + "─"*col_w + "┬" + "─"*col_n + "┬" + "─"*col_t + "┬" + "─"*col_s + "┤")
        lines.append(
            "│" + " Window".ljust(col_w) +
            "│" + " Habit".ljust(col_n) +
            "│" + " Type".ljust(col_t) +
            "│" + " Status".ljust(col_s) + "│"
        )

        for row in self.timetable_structure:
            lines.append(sep_row)
            for habit in row:
                window_label = f" {habit.preferred_window}"
                name_str     = f" {habit.habit_name}"
                type_str     = f" {habit.habit_type}"

                if habit.status == "complete":
                    status_str = " ✓ complete"
                elif habit.actual_start_time:
                    status_str = " ▶ in progress"
                else:
                    status_str = " ○ pending"

                lines.append(
                    "│" + window_label[:col_w].ljust(col_w) +
                    "│" + name_str[:col_n].ljust(col_n) +
                    "│" + type_str[:col_t].ljust(col_t) +
                    "│" + status_str[:col_s].ljust(col_s) + "│"
                )

                sched_str = f"  {habit.scheduled_start} – {habit.scheduled_end}"
                if habit.actual_start_time and habit.actual_end_time:
                    if habit.completion_history:
                        dur = habit.completion_history[-1].get("duration_mins")
                        dur_str = f" {dur} min" if dur is not None else ""
                    else:
                        dur_str = ""
                    detail_str = f" ↳ {habit.actual_start_time} → {habit.actual_end_time}{dur_str}"
                elif habit.actual_start_time:
                    detail_str = f" ↳ Started {habit.actual_start_time}"
                else:
                    detail_str = ""

                lines.append(
                    "│" + sched_str[:col_w].ljust(col_w) +
                    "│" + detail_str[:col_n].ljust(col_n) +
                    "│" + "".ljust(col_t) +
                    "│" + "".ljust(col_s) + "│"
                )

        lines.append(bot_row)
        return "\n".join(lines)