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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
