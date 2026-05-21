import os

class RewardManager:
    DEFAULT_REWARDS = [
        "Coffee break ☕", "15 min social media 📱", "Favourite snack 🍫",
        "Watch an episode 📺", "5 min stretch 🧘", "Call a friend 📞",
        "Short walk outside 🌿", "Listen to a favourite song 🎵",
    ]

    def assign_reward(self, habit) -> str:
        if habit.reward:
            return habit.reward
        import random
        chosen = random.choice(self.DEFAULT_REWARDS)
        habit.reward = chosen
        return chosen

    def verify_proof(self, image_path: str) -> bool:
        if not image_path or not os.path.exists(image_path):
            return False
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        _, ext = os.path.splitext(image_path.lower())
        return ext in valid_extensions