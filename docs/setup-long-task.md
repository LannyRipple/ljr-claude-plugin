# setup-long-task

A wizard for designing a resumable protocol directory for a long-running task — one
that spans multiple Claude sessions, compaction boundaries, or rate-limited APIs.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/setup-long-task](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/setup-long-task).

---

## The Core Idea

Some tasks are too large for a single Claude session: processing hundreds of items,
reading months of Slack history, scanning a large codebase. When compaction fires
mid-task, a fresh Claude needs to pick up exactly where the last one stopped — without
re-reading everything or re-querying a rate-limited API.

This skill interviews you about the task, determines which protocol elements you need,
creates the directory structure, and hands off with a populated RESUME.md that any
future Claude can follow cold.

See also: `/resume-long-task` to pick up a previously set up task.

---

## What Gets Created

The wizard always creates:

- **`GOAL.md`** — stable task description, success criteria, scope
- **`RESUME.md`** — current phase, what's done, and a literal next action

Based on your answers, it may also create:

- **Item inventory** (`progress.json`) — enumerable work queue with status
- **Results accumulator** (`findings.jsonl`) — append-only output, one record per item
- **Cursor file** (`cursor.txt`) — pagination position for APIs that paginate
- **Rate limit state** (`rate-limit.json`) — backoff tracking so a resumed session knows whether to wait
- **Error log** (`errors.jsonl`) — transient vs. permanent failures, separate from pending items
- **Session log** (`sessions.log`) — when each session ran and what it accomplished
- **Reconciliation script** (`check_progress.py`) — crosses inventory vs. accumulator to show pending items
- **Raw data cache** (e.g., `threads/`) — fetched source material for tasks where you might do multiple analysis passes

---

## Usage

```
/setup-long-task
"set up a long-running task to analyze 6 months of Slack messages"
"I need to process 500 GitHub issues across multiple sessions — help me set up a protocol"
```

The wizard asks one question at a time. For any service you name (Slack, GitHub, Splunk,
etc.), it applies its own knowledge of rate limits and pagination — you don't need to
know the vocabulary.

When the wizard finishes, it summarizes how the protocol elements work together for your
specific task and hands off. Review and adjust `GOAL.md` and `RESUME.md` before starting.

---

## Things Worth Knowing

**RESUME.md is the most important file.** It must contain a specific, literal next
action — not "continue processing" but "call `slack_read_thread` with ts=XYZ, append
result to findings.jsonl." A vague RESUME.md costs startup time every session.

**Rate-limited APIs: use CronCreate, not sleep.** When a backoff is long (minutes),
don't have Claude sit and wait — it ties up context and fails across compaction. Schedule
the next step with `CronCreate` and let Claude exit. The cron tick resumes from RESUME.md
at the right moment.

**The reconciliation pattern.** For large tasks, the inventory is written once and never
mutated. Completions are appended to the accumulator. A small script crosses the two.
This is safer than updating status in the inventory — appends can't corrupt partially
written JSON.

**The raw data cache.** If your task involves a rate-limited API and your analysis
question might evolve (first categorize, then count patterns, then re-examine a subset),
cache raw API responses locally. Re-reading local files is free; re-querying Slack is not.
