from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Optional

VALID_PRIORITIES = {"low", "medium", "high"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# How far out the next occurrence of a recurring task is due. timedelta handles
# month/year rollover correctly (e.g. Jan 31 + 1 day -> Feb 1), unlike manually
# incrementing a day/week number on the date.
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
VALID_FREQUENCIES = {"once", *RECURRENCE_INTERVALS}


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

    def mark_task_complete(self, task: "Task") -> Optional["Task"]:
        """Mark one of this pet's tasks complete, spawning its next occurrence if it recurs.

        Returns the newly created Task for the next occurrence, or None if the
        task was a one-off ("once") and nothing new was scheduled.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    frequency: str = "once"
    completed: bool = False
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None

    def __post_init__(self):
        """Validate that priority and frequency are allowed values."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got {self.priority!r}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}, got {self.frequency!r}")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, incomplete Task for this task's next occurrence.

        Returns None for a "once" task, since there is nothing to repeat.
        The new due_date is today's (or this task's) due_date plus the
        frequency's interval, via timedelta so month/year boundaries roll
        over correctly.
        """
        interval = RECURRENCE_INTERVALS.get(self.frequency)
        if interval is None:
            return None

        base_date = self.due_date or date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            scheduled_time=self.scheduled_time,
            due_date=base_date + interval,
        )


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

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Sort the current schedule by scheduled_time, unscheduled tasks last."""
        self.scheduled_tasks.sort(
            key=lambda pt: (pt[1].scheduled_time is None, pt[1].scheduled_time)
        )
        return self.scheduled_tasks

    def detect_conflicts(self) -> list[str]:
        """Return a warning message for every scheduled_time shared by 2+ tasks.

        A conflict is any pair of tasks scheduled at the same clock time, whether
        they belong to the same pet or different pets, since the owner can't
        physically do two tasks at once. Lightweight by design: groups tasks by
        scheduled_time in one O(n) pass instead of comparing every pair (O(n^2)),
        and returns plain strings for the caller to display rather than raising,
        so a conflicting schedule is still usable, just flagged.
        """
        by_time: dict[time, list[tuple[Pet, Task]]] = {}
        for pet, task in self.scheduled_tasks:
            if task.scheduled_time is None:
                continue
            by_time.setdefault(task.scheduled_time, []).append((pet, task))

        warnings = []
        for slot in sorted(by_time):
            pairs = by_time[slot]
            if len(pairs) < 2:
                continue
            names = ", ".join(f"[{pet.name}] {task.title}" for pet, task in pairs)
            warnings.append(f"Conflict at {slot.strftime('%H:%M')}: {names} are all scheduled at the same time.")
        return warnings

    def filter_tasks(
        self,
        *,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs across all of the owner's pets matching the given filters.

        Omit a filter to ignore it; pass both to require that a task match both.
        """
        results = self.owner.get_all_tasks()
        if completed is not None:
            results = [pt for pt in results if pt[1].completed == completed]
        if pet_name is not None:
            results = [pt for pt in results if pt[0].name == pet_name]
        return results

    def explain_plan(self) -> str:
        """Return a human-readable summary of the generated schedule."""
        if not self.scheduled_tasks:
            return "No tasks have been scheduled yet."

        lines = [f"Schedule for {self.date}:"]
        for pet, task in self.scheduled_tasks:
            lines.append(f"- [{pet.name}] {task.title} ({task.duration_minutes} min, {task.priority} priority)")

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.extend(f"WARNING: {warning}" for warning in conflicts)

        return "\n".join(lines)
