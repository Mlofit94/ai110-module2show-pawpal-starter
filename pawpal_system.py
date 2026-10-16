from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        pass

    def get_pets(self) -> list["Pet"]:
        pass


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner
    tasks: list["Task"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        pass

    def get_tasks(self) -> list["Task"]:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    completed: bool = False
    scheduled_time: time = None

    def mark_complete(self) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass


class Scheduler:
    def __init__(self, date: date, pet: Pet):
        self.date = date
        self.pet = pet

    def generate_schedule(self, tasks: list[Task], constraints: dict) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass
