import datetime
from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Jordan", preferences={"available_minutes": 60})

dog = Pet("Mochi", "dog", owner)
cat = Pet("Luna", "cat", owner)
owner.add_pet(dog)
owner.add_pet(cat)

# Added out of chronological order on purpose, to show sort_by_time() reordering them.
dog.add_task(Task("Evening walk", duration_minutes=20, priority="high", scheduled_time=time(18, 0)))
cat.add_task(
    Task(
        "Clean litter box",
        duration_minutes=15,
        priority="medium",
        frequency="daily",
        scheduled_time=time(9, 30),
        due_date=datetime.date.today(),
    )
)
dog.add_task(Task("Brush fur", duration_minutes=10, priority="low", scheduled_time=time(7, 0)))
cat.add_task(Task("Feed breakfast", duration_minutes=5, priority="high", scheduled_time=time(7, 30)))
# Scheduled at the same time as "Evening walk" on purpose, to demonstrate conflict detection.
cat.add_task(Task("Evening playtime", duration_minutes=15, priority="medium", scheduled_time=time(18, 0)))

scheduler = Scheduler(datetime.date.today(), owner)
scheduler.generate_schedule()
scheduler.sort_by_time()

print("Today's Schedule (sorted by time)")
print(scheduler.explain_plan())

# Mark one task complete to demonstrate status filtering.
dog.get_tasks()[1].mark_complete()  # "Brush fur"

print("\nRemaining (incomplete) tasks:")
for pet, task in scheduler.filter_tasks(completed=False):
    print(f"- [{pet.name}] {task.title}")

print("\nMochi's tasks only:")
for pet, task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"- {task.title} ({'done' if task.completed else 'pending'})")

# Completing a recurring task should spawn its next occurrence automatically.
litter_box = cat.get_tasks()[0]
next_task = cat.mark_task_complete(litter_box)
print(f"\nCompleted '{litter_box.title}' (due {litter_box.due_date}).")
if next_task is not None:
    print(f"Next occurrence auto-created: due {next_task.due_date}, completed={next_task.completed}")
print(f"Luna now has {len(cat.get_tasks())} tasks on file.")
