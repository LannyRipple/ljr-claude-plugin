# resume-long-task

Resumes a long-running task previously set up with `/setup-long-task`.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/resume-long-task](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/resume-long-task).

---

## What This Skill Does

Reads the task's `RESUME.md`, verifies that referenced files exist, checks whether a
rate-limit backoff is still in effect, reports current status, and begins the next action.

The skill is intentionally mechanical — it trusts that `RESUME.md` was written well by
`/setup-long-task` and the previous session. Its job is to get to work fast with minimal
startup cost.

---

## Usage

```
/resume-long-task ~/tmp/my-task/
/resume-long-task
"pick up where we left off on the Slack analysis"
"continue the GitHub issues task"
```

If you don't provide a path, the skill asks for one.

---

## What It Checks on Resume

1. **File existence** — parses RESUME.md for referenced filenames and confirms they exist.
   Missing files are reported before any work starts, with options to continue without them
   or abort and re-run `/setup-long-task`.

2. **Rate limit state** — if `rate-limit.json` exists, calculates remaining backoff.
   If a wait is still in effect, reports it and suggests scheduling with CronCreate rather
   than waiting inline.

3. **Status report** — reads `GOAL.md` then `RESUME.md` and summarizes: what phase,
   what's done, what's pending, and the next action.

---

## Things Worth Knowing

**This skill is only as good as RESUME.md.** If the previous session ended without
updating RESUME.md, the resume point may be stale. Check the Next Action section before
confirming you want to proceed.

**CronCreate is your friend for rate limits.** If a backoff is still running when you
invoke this skill, don't wait — use CronCreate to schedule the resume and close the
session. The cron tick will invoke this skill again when the window clears.

**Checkpoints matter.** After completing each item, the skill writes RESUME.md before
continuing. If compaction fires mid-task, the next session resumes from the last
checkpoint — not from the beginning of the batch.
