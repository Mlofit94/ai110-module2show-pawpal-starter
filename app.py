import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+ — a pet care planning assistant. Add tasks below, then build
today's schedule to see them sorted by time, checked for conflicts, and filtered
by status or pet.
"""
)

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
owner = st.session_state.owner
owner.name = owner_name  # keep in sync with the text input on every rerun

if "pet" not in st.session_state:
    pet = Pet(pet_name, species, owner)
    owner.add_pet(pet)
    st.session_state.pet = pet
pet = st.session_state.pet
pet.name = pet_name  # keep in sync with the text input on every rerun
pet.species = species

scheduler = Scheduler(datetime.date.today(), owner)


def _task_row(pet_obj: Pet, task: Task) -> dict:
    return {
        "time": task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "—",
        "owner": pet_obj.owner.name,
        "pet": pet_obj.name,
        "task": task.title,
        "duration_minutes": task.duration_minutes,
        "priority": task.priority,
        "frequency": task.frequency,
        "status": "done" if task.completed else "pending",
    }


st.markdown("### Tasks")
st.caption("Add a few tasks. These are stored on the pet and feed into the scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])

has_time = st.checkbox("Give it a specific time of day", value=True)
scheduled_time = st.time_input("Time", value=datetime.time(9, 0)) if has_time else None

if st.button("Add task"):
    pet.add_task(
        Task(
            task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            scheduled_time=scheduled_time,
            due_date=datetime.date.today(),
        )
    )

if pet.get_tasks():
    st.write("Current tasks:")
    st.table([_task_row(pet, t) for t in pet.get_tasks()])

    incomplete = [t for t in pet.get_tasks() if not t.completed]
    if incomplete:
        def _task_label(t: Task) -> str:
            when = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "no time set"
            return f"{t.title} — {pet.name} — {when} — {t.duration_minutes} min — {t.priority} priority"

        selected_index = st.selectbox(
            "Mark a task complete",
            options=range(len(incomplete)),
            format_func=lambda i: _task_label(incomplete[i]),
        )
        if st.button("Mark complete"):
            task = incomplete[selected_index]
            next_task = pet.mark_task_complete(task)
            if next_task is not None:
                st.success(f"'{task.title}' completed — next occurrence due {next_task.due_date}.")
            else:
                st.success(f"'{task.title}' marked complete.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Filter Tasks")
status_choice = st.radio("Status", ["All", "Pending", "Completed"], horizontal=True)
completed_filter = {"All": None, "Pending": False, "Completed": True}[status_choice]

filtered = scheduler.filter_tasks(completed=completed_filter, pet_name=pet.name)
if filtered:
    st.table([_task_row(p, t) for p, t in filtered])
else:
    st.info("No tasks match this filter.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's schedule, sorted by time, with conflicts flagged.")

if st.button("Generate schedule"):
    scheduler.generate_schedule()
    scheduler.sort_by_time()
    conflicts = scheduler.detect_conflicts()

    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("Schedule generated — no time conflicts detected.")

    if scheduler.scheduled_tasks:
        st.table([_task_row(p, t) for p, t in scheduler.scheduled_tasks])
    else:
        st.info("Nothing fit in today's schedule — add tasks or raise the time budget.")
