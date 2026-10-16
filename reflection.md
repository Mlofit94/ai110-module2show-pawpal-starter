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

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to help brainstorm my classes, turn my UML into Python code, and review my code for problems. The AI suggested things like adding a `scheduled_tasks` list to the Scheduler so it could remember its plan, and a `get_all_tasks()` method on Owner so the Scheduler could pull tasks from all pets instead of just one. Asking it to review my code and explain issues in plain language was the most helpful.

**b. Judgment and verification**

The AI first gave the Scheduler its own separate `tasks` list, but I didn't accept that — it would have duplicated the tasks already stored on each Pet. I had it remove that field so tasks only live in one place. I verified everything worked by running `main.py` and checking that the printed schedule looked correct, and by running the pytest tests to confirm task completion and task addition both worked as expected.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
