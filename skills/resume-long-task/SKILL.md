---
name: resume-long-task
description: >-
  Resumes a long-running task previously set up with /setup-long-task. Trigger when
  the user says /resume-long-task, provides a path to a task directory or RESUME.md,
  says they want to continue a previously set-up long-running task, or says "pick up
  where we left off," "continue the [task name] task," or provides a task directory
  path unprompted.
---

# resume-long-task

Before proceeding, read `${CLAUDE_PLUGIN_ROOT}/skills/setup-long-task/references/protocol-elements.md`
for definitions of all protocol files referenced in the steps below.

---

## Step 1: Locate RESUME.md

If the user provided a path to a task directory or RESUME.md, use it. Otherwise ask:
"What is the path to your task directory or RESUME.md?"

If given a directory, look for `RESUME.md` inside it.

---

## Step 2: Sanity check

Before reading RESUME.md in depth, parse it for filenames (inventory, accumulator,
cursor, rate-limit, helper scripts). For each filename found, confirm the file exists
in the task directory. A missing file surfaces now, not mid-task. Report any missing
files to the user and offer: (a) continue with the files that exist, or (b) abort and
re-run /setup-long-task to regenerate missing files.

---

## Step 3: Check rate limit state

If `rate-limit.json` does not exist, proceed to Step 4 — no rate-limit constraint is
in effect.

If it exists, read it and compute: `elapsed = current_time - last_call_ts (in seconds)`.
If `elapsed < backoff_seconds`, a wait is still in effect; `remaining = backoff_seconds - elapsed`.
Report clearly: "Rate limit: {N} minutes remaining." If a CronCreate was already
scheduled for this task, it will fire at the right time — no action needed. Otherwise
use CronCreate to schedule resume. Waiting is not recommended for backoffs over a few
minutes — it ties up context and fails across compaction.

Do not proceed with any API calls if the backoff has not cleared.

---

## Step 4: Orient and report

Read `GOAL.md` first (task description and success criteria), then `RESUME.md` (current
state and next action). Report to the user:
- Current phase and what has been completed
- What is pending
- Any active rate limit constraint
- The next action

---

## Step 5: Begin

Execute the Next Action from RESUME.md. A checkpoint is: completing one item, hitting
a rate limit, or reaching a phase boundary. Write RESUME.md before taking any action
that could result in a stop (rate limit, compaction, or task end). After updating
RESUME.md, re-read it to confirm the next action before continuing — this ensures a
compaction mid-loop resumes cleanly.
