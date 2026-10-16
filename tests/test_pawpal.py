from pawpal_system import Owner, Pet, Task


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
