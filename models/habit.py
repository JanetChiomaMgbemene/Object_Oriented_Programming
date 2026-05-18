from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Habit:
    name: str
    description: str = ""
    frequency: str = "daily"  # daily, weekly, monthly
    target: int = 1
    streak: int = 0
    created_at: date = field(default_factory=date.today)
    last_completed: Optional[date] = None
    active: bool = True

    def complete(self, completed_on: Optional[date] = None) -> None:
        completed_on = completed_on or date.today()
        if self.last_completed == completed_on:
            return

        if self._is_consecutive(completed_on):
            self.streak += 1
        else:
            self.streak = 1

        self.last_completed = completed_on

    def _is_consecutive(self, completed_on: date) -> bool:
        if self.last_completed is None:
            return False

        if self.frequency == "daily":
            return completed_on == self.last_completed + timedelta(days=1)
        if self.frequency == "weekly":
            return completed_on <= self.last_completed + timedelta(days=7)
        if self.frequency == "monthly":
            return (
                completed_on.year == self.last_completed.year
                and completed_on.month == self.last_completed.month + 1
            )

        return False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "target": self.target,
            "streak": self.streak,
            "created_at": self.created_at.isoformat(),
            "last_completed": self.last_completed.isoformat()
            if self.last_completed
            else None,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Habit":
        last_completed = (
            date.fromisoformat(data["last_completed"])
            if data.get("last_completed")
            else None
        )
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            frequency=data.get("frequency", "daily"),
            target=data.get("target", 1),
            streak=data.get("streak", 0),
            created_at=date.fromisoformat(data.get("created_at", date.today().isoformat())),
            last_completed=last_completed,
            active=data.get("active", True),
        )