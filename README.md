# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:
- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Priority-based scheduling** — builds a day's plan across every pet an owner has, picking tasks by priority first and fitting as many as possible within an optional time budget, without blocking smaller lower-priority tasks behind one that didn't fit.
- **Sorting by time** — orders the generated schedule chronologically by each task's time of day, with any task that has no time set pushed to the end instead of breaking the sort.
- **Filtering by status or pet** — narrows the task list down to just completed/pending tasks, a single pet, or both at once.
- **Conflict warnings** — flags any two tasks scheduled for the exact same time (whether for the same pet or different pets) with a clear, human-readable warning naming which tasks collide and when, so an owner can resolve it before the day starts.
- **Daily/weekly recurrence** — completing a recurring task automatically creates its next occurrence with the correct due date (handling month- and year-end rollovers correctly), while one-off tasks simply stay completed.

## Implementation Summary

PawPal+ is built around four classes in `pawpal_system.py`:

- **Owner** holds a name, preferences, and a list of `Pet`s. It can add pets and, importantly, collect every pet's tasks together via `get_all_tasks()`.
- **Pet** holds basic info (name, species) and its own list of `Task`s.
- **Task** represents a single care activity — title, duration, priority, frequency, and completion status — and validates that its priority is one of `low`/`medium`/`high`.
- **Scheduler** is the "brain." It never looks at a single pet directly — it goes through `Owner.get_all_tasks()` so it can build a plan across *all* of an owner's pets at once. It sorts pending tasks by priority and duration, fills the day up to an optional time budget, and can explain the resulting plan in plain text.

`main.py` ties it together as a quick CLI demo: it creates an owner with two pets, adds a few tasks, generates a schedule, and prints it — see the Sample Output section above.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
Schedule for 2026-10-15:
- [Mochi] Morning walk (20 min, high priority)
- [Luna] Clean litter box (15 min, medium priority)
- [Mochi] Brush fur (10 min, low priority)
```

## 🧪 Testing PawPal+

`tests/test_pawpal.py` covers the core scheduling behaviors with both happy-path and edge-case checks:

- **Scheduling** — tasks are picked by priority within the time budget, an oversized task is skipped without blocking smaller ones later, and an empty task list doesn't crash.
- **Sorting** — `sort_by_time()` orders tasks chronologically, pushes unscheduled tasks to the end, and handles duplicate times without error.
- **Filtering** — `filter_tasks()` narrows by completion status and/or pet name, returning `[]` instead of erroring when nothing matches.
- **Conflict detection** — `detect_conflicts()` flags tasks sharing the same time (same pet or across pets) and ignores unscheduled tasks.
- **Recurring tasks** — completing a `"daily"`/`"weekly"` task spawns the correctly dated next occurrence (including month/year rollovers), `"once"` tasks don't recur, and invalid frequencies raise an error. One test documents a known gap: completing an already-completed recurring task currently creates a duplicate next occurrence.

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
tests/test_pawpal.py::test_task_completion_changes_status PASSED        [  4%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED  [  8%]
tests/test_pawpal.py::test_generate_schedule_respects_priority_and_budget PASSED [ 12%]
tests/test_pawpal.py::test_generate_schedule_continues_past_oversized_task PASSED [ 16%]
tests/test_pawpal.py::test_generate_schedule_with_no_tasks PASSED       [ 20%]
tests/test_pawpal.py::test_sort_by_time_orders_ascending PASSED         [ 25%]
tests/test_pawpal.py::test_sort_by_time_pushes_unscheduled_tasks_last PASSED [ 29%]
tests/test_pawpal.py::test_sort_by_time_handles_identical_times_without_error PASSED [ 33%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED     [ 37%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED              [ 41%]
tests/test_pawpal.py::test_filter_tasks_with_no_matches_returns_empty_list PASSED [ 45%]
tests/test_pawpal.py::test_filter_tasks_with_no_tasks_at_all PASSED     [ 50%]
tests/test_pawpal.py::test_detect_conflicts_returns_empty_when_no_overlap PASSED [ 54%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_across_pets PASSED [ 58%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_within_one_pet PASSED [ 62%]
tests/test_pawpal.py::test_detect_conflicts_ignores_unscheduled_tasks PASSED [ 66%]
tests/test_pawpal.py::test_mark_task_complete_once_task_does_not_recur PASSED [ 70%]
tests/test_pawpal.py::test_mark_task_complete_daily_task_creates_next_occurrence PASSED [ 75%]
tests/test_pawpal.py::test_mark_task_complete_weekly_task_adds_seven_days PASSED [ 79%]
tests/test_pawpal.py::test_recurring_task_with_no_due_date_defaults_to_today PASSED [ 83%]
tests/test_pawpal.py::test_recurring_task_rolls_over_month_boundary PASSED [ 87%]
tests/test_pawpal.py::test_recurring_task_rolls_over_year_boundary_weekly PASSED [ 91%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error PASSED  [ 95%]
tests/test_pawpal.py::test_calling_mark_task_complete_twice_spawns_duplicate_next_occurrence PASSED [100%]
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts the generated schedule by each task's `scheduled_time`; tasks with no time set are pushed to the end instead of crashing the sort. |
| Filtering | `Scheduler.filter_tasks()` | Filters tasks across all of an owner's pets by completion status, pet name, or both (omit either to skip that filter). |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups scheduled tasks by `scheduled_time` and flags any time slot shared by 2+ tasks (same pet or different pets) as a warning string — exact-time matches only, not overlapping durations. Warnings are appended automatically in `explain_plan()`. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Completing a `"daily"` or `"weekly"` task via `Pet.mark_task_complete()` creates and adds the next occurrence automatically, with its `due_date` advanced by `timedelta` (so month/year boundaries roll over correctly). `"once"` tasks don't recur. |

## 📸 Demo Walkthrough

### UI features

The Streamlit app (`app.py`) lets a user:

- Enter an owner name, pet name, and species, which update the underlying `Owner`/`Pet` live as you type.
- Add a task with a title, duration, priority, repeat frequency (`once`/`daily`/`weekly`), and an optional time of day.
- View all of a pet's tasks in a table (time, owner, pet, task, duration, priority, frequency, status).
- Mark a task complete from a dropdown that labels each option with enough detail (pet, time, duration, priority) to tell tasks apart, even when titles repeat.
- Filter the task list by status (All/Pending/Completed).
- Generate today's schedule, which sorts it by time and checks it for conflicts before displaying it.

### Example workflow

1. Add a pet — type an owner and pet name at the top; a `Pet` is created and tracked for the rest of the session.
2. Add a task — e.g. "Morning walk," 20 minutes, high priority, at 09:00. It appears immediately in the "Current tasks" table.
3. Add a second task at the same time (e.g. "Feed breakfast" also at 09:00) to see conflict detection in action.
4. Click **Generate schedule** — the app sorts both tasks by time and shows a warning that they collide at 09:00, followed by the full sorted schedule.
5. Mark a task complete — if it's a `"daily"` or `"weekly"` task, a new occurrence is created automatically for the next due date, visible in the task count and table.

### Key Scheduler behaviors shown

- **Sorting** — `sort_by_time()` always presents the day in chronological order, regardless of the order tasks were entered.
- **Conflict warnings** — `detect_conflicts()` catches same-time collisions across pets (not just within one pet) and reports them in plain language before the schedule table.
- **Filtering** — `filter_tasks()` narrows what's shown without losing any underlying data; switching the status filter never deletes a task.
- **Recurrence** — `Pet.mark_task_complete()` keeps recurring tasks alive by generating the next occurrence the moment the current one is completed, rather than requiring the user to re-enter it.

### Sample CLI output

Running `python main.py` exercises the same Scheduler logic outside the UI:

```
Today's Schedule (sorted by time)
Schedule for 2026-10-16:
- [Luna] Feed breakfast (5 min, high priority)
- [Luna] Clean litter box (15 min, medium priority)
- [Mochi] Evening walk (20 min, high priority)
- [Luna] Evening playtime (15 min, medium priority)

WARNING: Conflict at 18:00: [Mochi] Evening walk, [Luna] Evening playtime are all scheduled at the same time.

Remaining (incomplete) tasks:
- [Mochi] Evening walk
- [Luna] Clean litter box
- [Luna] Feed breakfast
- [Luna] Evening playtime

Mochi's tasks only:
- Evening walk (pending)
- Brush fur (done)

Completed 'Clean litter box' (due 2026-10-16).
Next occurrence auto-created: due 2026-10-17, completed=False
Luna now has 4 tasks on file.
```
