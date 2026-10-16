# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Owner — holds a name, preferences, and their list of pets; responsible for managing which pets it owns.

Pet — holds name, species, owner reference, and its list of tasks; responsible for tracking its own care tasks.

Task — holds title, duration, priority, completion status, scheduled time; responsible for its own completion state and priority check.

Scheduler — holds a date and a pet; responsible for building and explaining the daily task schedule (doesn't store tasks itself — receives them when generating a schedule).
------------------------------------------------------------------
1. Add a pet profile — everything else (walks, tasks, reminders) depends on having a pet to attach it to.

2. Schedule a walk — it's the app's core recurring use case, the reason someone opens PawPal day to day.

3. See today's tasks — gives an at-a-glance view so users can quickly check what's done/pending without digging through screens.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

1. The Scheduler now has a place to store the schedule it builds, so it can later explain why it picked those tasks.
2. Instead of being handed a random list of tasks, the Scheduler now just looks at the pet's own task list — no more risk of using the wrong set of tasks.
3. The Scheduler is now connected to the Owner, so it can actually see things like how much time the owner has available when building a plan.
4. A task's scheduled time is now clearly marked as "optional," since a task might not have a time assigned yet.
5. Fixed a printing/comparison issue caused by the Pet and Owner referring back to each other — that loop no longer confuses Python.
6. Added a safety check so a task's priority can only be "low," "medium," or "high" — typos like "hgih" will now throw an error instead of silently breaking later.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`detect_conflicts()` only flags tasks scheduled at the *exact same* time, not tasks whose durations overlap (e.g. a 20-minute task at 9:00 and another starting at 9:10 wouldn't be caught, even though they overlap). I chose this because it's simple and fast to check — just group tasks by their time and flag any group with more than one — whereas true overlap detection means comparing start/end ranges between every pair of tasks, which is more code and slower to run. For a single pet owner's daily task list (a handful of tasks), exact-match conflicts are the obvious case to catch first, and the missed overlap cases are a known limitation rather than a bug.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to help brainstorm my classes, turn my UML into Python code, and review my code for problems. The AI suggested things like adding a `scheduled_tasks` list to the Scheduler so it could remember its plan, and a `get_all_tasks()` method on Owner so the Scheduler could pull tasks from all pets instead of just one. Asking it to review my code and explain issues in plain language was the most helpful.

**b. Judgment and verification**

The AI first gave the Scheduler its own separate `tasks` list, but I didn't accept that — it would have duplicated the tasks already stored on each Pet. I had it remove that field so tasks only live in one place. I verified everything worked by running `main.py` and checking that the printed schedule looked correct, and by running the pytest tests to confirm task completion and task addition both worked as expected.

**c. AI Strategy**

- *Most effective features:* Plain-language code review (catching bugs and explaining *why* they're bugs), writing test cases for edge cases I wouldn't have thought of, and actually running the app/tests to check things worked instead of just assuming the code was right.
- *A suggestion I rejected:* The AI gave the Scheduler its own copy of the task list. I said no — tasks should only live in one place (on the Pet), so I had it removed. Small change, but it kept the design from having two "sources of truth" for the same data.
- *Separate chat sessions:* Working through one feature at a time (design, then sorting, then recurring tasks, then conflicts, then tests, then UI) kept each conversation focused. It meant feedback stayed on-topic instead of mixing half-finished ideas from different parts of the project together.
- *Being the "lead architect":* The AI is good at generating options and catching mistakes, but it doesn't know what I actually want my app to look like — that's still my call. My job was to approve, reject, or simplify what it suggested, and to double-check its work rather than trust it blindly.

---

## 4. Testing and Verification

**a. What you tested**

I wrote pytest tests for every main feature: building a schedule (priority + time budget), sorting by time, filtering by status/pet, conflict detection, and recurring tasks. I tested both the normal case (everything works as expected) and edge cases, like an empty task list, two tasks at the exact same time, a task with no time set, and a recurring task's due date rolling over a month or year boundary. These mattered because the "normal" case is easy to get right by accident, it's the edge cases (nothing scheduled, times colliding, dates rolling over) where real bugs hide.

**b. Confidence**

I'm fairly confident the core logic is correct, all 24 tests pass, covering both happy paths and the edge cases above. The one thing I'm not confident about: completing an already-completed recurring task currently creates a duplicate "next day" task instead of being blocked. I wrote a test that documents this as a known gap rather than pretending it's fixed. If I had more time, I'd also test true overlapping-time conflicts (not just exact-same-time matches) and add tests for multiple pets interacting on the same schedule.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the four features — sorting, filtering, conflict detection, and recurring tasks — all work together through the same `Scheduler` class without stepping on each other. Each one is simple on its own, but combined they make the schedule feel genuinely useful instead of just a sorted list.

**b. What you would improve**

I'd fix the duplicate-task bug from completing an already-completed recurring task, and upgrade conflict detection to catch overlapping durations, not just exact time matches. I'd also extend the UI to support more than one pet at a time, since right now it only tracks a single pet per session.

**c. Key takeaway**

The AI was great at generating code, catching bugs, and writing tests fast — but it doesn't know what I actually want the app to be. The real work was deciding what to accept, what to simplify, and what to verify myself by actually running the app and tests, instead of assuming the code was correct just because it looked reasonable.
