from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_changes_status():
    task = Task("Morning walk", duration_minutes=20, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Brush fur", duration_minutes=10, priority="low"))

    assert len(pet.get_tasks()) == 1


# --- Scheduling (generate_schedule) ---


def test_generate_schedule_respects_priority_and_budget():
    owner = Owner("Jordan", preferences={"available_minutes": 30})
    dog = Pet("Mochi", "dog", owner)
    cat = Pet("Luna", "cat", owner)
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Walk", duration_minutes=20, priority="high"))
    cat.add_task(Task("Feed", duration_minutes=5, priority="high"))
    cat.add_task(Task("Play", duration_minutes=15, priority="low"))

    scheduler = Scheduler(date.today(), owner)
    scheduled = scheduler.generate_schedule()

    # Feed (high, 5 min) + Walk (high, 20 min) = 25 min fits in 30; Play would push it to 40.
    assert [task.title for task in scheduled] == ["Feed", "Walk"]


def test_generate_schedule_continues_past_oversized_task():
    owner = Owner("Jordan", preferences={"available_minutes": 20})
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("Big high-priority task", duration_minutes=30, priority="high"))
    pet.add_task(Task("Small low-priority task", duration_minutes=10, priority="low"))

    scheduler = Scheduler(date.today(), owner)
    scheduled = scheduler.generate_schedule()

    # The oversized high-priority task is skipped, but the smaller low-priority
    # task after it still gets scheduled (continue, not break).
    assert [task.title for task in scheduled] == ["Small low-priority task"]


def test_generate_schedule_with_no_tasks():
    owner = Owner("Jordan")
    scheduler = Scheduler(date.today(), owner)

    scheduled = scheduler.generate_schedule()

    assert scheduled == []
    assert scheduler.explain_plan() == "No tasks have been scheduled yet."


# --- Sorting (sort_by_time) ---


def test_sort_by_time_orders_ascending():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("Evening", duration_minutes=10, priority="low", scheduled_time=time(18, 0)))
    pet.add_task(Task("Morning", duration_minutes=10, priority="low", scheduled_time=time(7, 0)))
    pet.add_task(Task("Midday", duration_minutes=10, priority="low", scheduled_time=time(12, 0)))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()
    scheduler.sort_by_time()

    titles = [task.title for _pet, task in scheduler.scheduled_tasks]
    assert titles == ["Morning", "Midday", "Evening"]


def test_sort_by_time_pushes_unscheduled_tasks_last():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("No time", duration_minutes=10, priority="low"))
    pet.add_task(Task("Has time", duration_minutes=10, priority="low", scheduled_time=time(9, 0)))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()
    scheduler.sort_by_time()

    titles = [task.title for _pet, task in scheduler.scheduled_tasks]
    assert titles == ["Has time", "No time"]


def test_sort_by_time_handles_identical_times_without_error():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("First", duration_minutes=10, priority="low", scheduled_time=time(9, 0)))
    pet.add_task(Task("Second", duration_minutes=10, priority="low", scheduled_time=time(9, 0)))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()
    scheduler.sort_by_time()  # should not raise

    assert len(scheduler.scheduled_tasks) == 2


# --- Filtering (filter_tasks) ---


def test_filter_tasks_by_completion_status():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    done = Task("Done", duration_minutes=5, priority="low")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Pending", duration_minutes=5, priority="low"))

    scheduler = Scheduler(date.today(), owner)
    incomplete = scheduler.filter_tasks(completed=False)

    assert [task.title for _pet, task in incomplete] == ["Pending"]


def test_filter_tasks_by_pet_name():
    owner = Owner("Jordan")
    dog = Pet("Mochi", "dog", owner)
    cat = Pet("Luna", "cat", owner)
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Walk", duration_minutes=10, priority="low"))
    cat.add_task(Task("Feed", duration_minutes=10, priority="low"))

    scheduler = Scheduler(date.today(), owner)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")

    assert [task.title for _pet, task in mochi_tasks] == ["Walk"]


def test_filter_tasks_with_no_matches_returns_empty_list():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", duration_minutes=10, priority="low"))

    scheduler = Scheduler(date.today(), owner)

    assert scheduler.filter_tasks(pet_name="Nonexistent") == []
    assert scheduler.filter_tasks(completed=True, pet_name="Mochi") == []


def test_filter_tasks_with_no_tasks_at_all():
    owner = Owner("Jordan")
    scheduler = Scheduler(date.today(), owner)

    assert scheduler.filter_tasks() == []


# --- Conflict detection (detect_conflicts) ---


def test_detect_conflicts_returns_empty_when_no_overlap():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", duration_minutes=10, priority="low", scheduled_time=time(9, 0)))
    pet.add_task(Task("Feed", duration_minutes=10, priority="low", scheduled_time=time(10, 0)))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_flags_same_time_across_pets():
    owner = Owner("Jordan")
    dog = Pet("Mochi", "dog", owner)
    cat = Pet("Luna", "cat", owner)
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Walk", duration_minutes=10, priority="low", scheduled_time=time(18, 0)))
    cat.add_task(Task("Play", duration_minutes=10, priority="low", scheduled_time=time(18, 0)))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "18:00" in warnings[0]
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


def test_detect_conflicts_flags_same_time_within_one_pet():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", duration_minutes=10, priority="low", scheduled_time=time(9, 0)))
    pet.add_task(Task("Brush", duration_minutes=10, priority="low", scheduled_time=time(9, 0)))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()

    assert len(scheduler.detect_conflicts()) == 1


def test_detect_conflicts_ignores_unscheduled_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    pet.add_task(Task("No time A", duration_minutes=10, priority="low"))
    pet.add_task(Task("No time B", duration_minutes=10, priority="low"))

    scheduler = Scheduler(date.today(), owner)
    scheduler.generate_schedule()

    assert scheduler.detect_conflicts() == []


# --- Recurring tasks (Task.next_occurrence / Pet.mark_task_complete) ---


def test_mark_task_complete_once_task_does_not_recur():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    task = Task("One-time vet visit", duration_minutes=30, priority="high")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task)

    assert next_task is None
    assert task.completed is True
    assert len(pet.get_tasks()) == 1


def test_mark_task_complete_daily_task_creates_next_occurrence():
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat", owner)
    owner.add_pet(pet)
    task = Task(
        "Clean litter box",
        duration_minutes=15,
        priority="medium",
        frequency="daily",
        due_date=date(2026, 10, 15),
    )
    pet.add_task(task)

    next_task = pet.mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == date(2026, 10, 16)
    assert next_task.completed is False
    assert len(pet.get_tasks()) == 2


def test_mark_task_complete_weekly_task_adds_seven_days():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    task = Task(
        "Grooming",
        duration_minutes=45,
        priority="medium",
        frequency="weekly",
        due_date=date(2026, 10, 1),
    )
    pet.add_task(task)

    next_task = pet.mark_task_complete(task)

    assert next_task.due_date == date(2026, 10, 8)


def test_recurring_task_with_no_due_date_defaults_to_today():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    task = Task("Feed", duration_minutes=5, priority="high", frequency="daily")

    next_task = pet.mark_task_complete(task)

    assert next_task.due_date == date.today() + timedelta(days=1)


def test_recurring_task_rolls_over_month_boundary():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    task = Task(
        "Feed",
        duration_minutes=5,
        priority="high",
        frequency="daily",
        due_date=date(2026, 1, 31),
    )

    next_task = pet.mark_task_complete(task)

    assert next_task.due_date == date(2026, 2, 1)


def test_recurring_task_rolls_over_year_boundary_weekly():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", owner)
    owner.add_pet(pet)
    task = Task(
        "Grooming",
        duration_minutes=30,
        priority="medium",
        frequency="weekly",
        due_date=date(2026, 12, 28),
    )

    next_task = pet.mark_task_complete(task)

    assert next_task.due_date == date(2027, 1, 4)


def test_invalid_frequency_raises_value_error():
    with pytest.raises(ValueError):
        Task("Mystery", duration_minutes=10, priority="low", frequency="monthly")


def test_calling_mark_task_complete_twice_spawns_duplicate_next_occurrence():
    """Documents a known gap: completing an already-completed recurring task spawns
    another next-occurrence from the same due_date, since due_date doesn't change on
    completion. Not guarded against yet -- this pins down current behavior rather
    than asserting it's correct.
    """
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat", owner)
    owner.add_pet(pet)
    task = Task(
        "Clean litter box",
        duration_minutes=15,
        priority="medium",
        frequency="daily",
        due_date=date(2026, 10, 15),
    )
    pet.add_task(task)

    first_next = pet.mark_task_complete(task)
    second_next = pet.mark_task_complete(task)

    assert first_next.due_date == date(2026, 10, 16)
    assert second_next.due_date == date(2026, 10, 16)
    assert len(pet.get_tasks()) == 3
