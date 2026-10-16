from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

VALID_PRIORITIES = {"low", "medium", "high"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pets(self) -> list["Pet"]:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> list[tuple["Pet", "Task"]]:
        """Flatten every pet's tasks into (pet, task) pairs."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet, task))
        return all_tasks


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner = field(repr=False, compare=False)
    tasks: list["Task"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        """Add a task to this pet's list of tasks."""
        self.tasks.append(task)

    def get_tasks(self) -> list["Task"]:
        """Return this pet's list of tasks."""
        return self.tasks


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    frequency: str = "once"
    completed: bool = False
    scheduled_time: Optional[time] = None

    def __post_init__(self):
        """Validate that priority is one of the allowed values."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"


class Scheduler:
    """The 'brain' that organizes tasks across ALL of an owner's pets.

    It never reads from a single Pet directly — it always goes through
    Owner.get_all_tasks(), so a plan can include every pet, not just one.
    """

    def __init__(self, date: date, owner: Owner):
        """Create a scheduler for the given date and owner."""
        self.date = date
        self.owner = owner
        self.scheduled_tasks: list[tuple[Pet, Task]] = []

    def generate_schedule(self, constraints: Optional[dict] = None) -> list[Task]:
        """Build and store today's task schedule across all of the owner's pets."""
        constraints = {**self.owner.preferences, **(constraints or {})}
        available_minutes = constraints.get("available_minutes")

        pending = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed
        ]
        pending.sort(
            key=lambda pt: (PRIORITY_ORDER.get(pt[1].priority, 3), pt[1].duration_minutes)
        )

        scheduled = []
        total_minutes = 0
        for pet, task in pending:
            if available_minutes is not None and total_minutes + task.duration_minutes > available_minutes:
                continue
            scheduled.append((pet, task))
            total_minutes += task.duration_minutes

        self.scheduled_tasks = scheduled
        return [task for _pet, task in scheduled]

    def explain_plan(self) -> str:
        """Return a human-readable summary of the generated schedule."""
        if not self.scheduled_tasks:
            return "No tasks have been scheduled yet."

        lines = [f"Schedule for {self.date}:"]
        for pet, task in self.scheduled_tasks:
            lines.append(f"- [{pet.name}] {task.title} ({task.duration_minutes} min, {task.priority} priority)")
        return "\n".join(lines)
