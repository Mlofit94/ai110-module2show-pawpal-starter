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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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
