import datetime

from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Jordan", preferences={"available_minutes": 60})

dog = Pet("Mochi", "dog", owner)
cat = Pet("Luna", "cat", owner)
owner.add_pet(dog)
owner.add_pet(cat)

dog.add_task(Task("Morning walk", duration_minutes=20, priority="high"))
dog.add_task(Task("Brush fur", duration_minutes=10, priority="low"))
cat.add_task(Task("Clean litter box", duration_minutes=15, priority="medium"))

scheduler = Scheduler(datetime.date.today(), owner)
scheduler.generate_schedule()

print("Today's Schedule")
print(scheduler.explain_plan())
