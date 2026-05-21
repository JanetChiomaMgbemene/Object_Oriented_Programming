import random

class CongratManager:    # Generates motivational messages when habits are completed.

    MESSAGES = [
        "Amazing work! Keep it up! 🔥",
        "You're building a great habit! 💪",
        "Streak growing — don't stop now! ⚡",
        "Consistency is key and you have it! 🏆",
        "One step closer to your best self! 🌟",
        "Small steps lead to big changes! 🚀",
        "You showed up — that's what matters! 👏",
        "Progress, not perfection! Keep going! 🎯",
    ]

    def generate_message(self, habit) -> str:        # Returns a personalised message using the habit name and streak.
        streak = habit.current_streak
        streak_note = f" ({streak}-day streak! 🔥)" if streak > 1 else ""
        base = random.choice(self.MESSAGES)
        return f"Great job completing '{habit.habit_name}'!{streak_note}\n{base}"

    def get_random_message(self) -> str:        # Returns a random message.
        return random.choice(self.MESSAGES)

    def get_custom_message(self, habit) -> str:
        # Returns the habit's custom message if set, else a generated one.
        if habit.custom_message:
            return habit.custom_message
        return self.generate_message(habit)