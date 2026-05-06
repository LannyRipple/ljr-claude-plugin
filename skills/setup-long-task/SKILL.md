---
name: setup-long-task
description: >-
  Collaborative wizard for designing a resumable protocol directory for a long-running
  task — one that spans multiple Claude sessions, compaction boundaries, or rate-limited
  APIs. Trigger when the user describes a task that involves processing many items,
  reading a large data source, working around API rate limits, or any work expected to
  take multiple sessions. Also trigger on /setup-long-task.
---

# setup-long-task

Your job is to help the user design and create a resumable protocol directory for a
long-running task. You gather enough information to determine which protocol elements
the task needs, create the directory and files, then hand off.

## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow unless you have a specific
  reason not to; note when you deviate and why.

Every MUST and SHOULD in this skill is paired with a rationale.

---

## Step 1: Load protocol element reference

Read `${CLAUDE_SKILL_DIR}/references/protocol-elements.md` before doing anything else.
It defines all available protocol elements, when each is needed, and contains a case
study. Keep this in mind throughout the wizard.

---

## Step 2: Capture task description

If the current conversation already contains a task description, extract it. Otherwise
ask: "Describe the task — what are you trying to accomplish, and what does success look
like?"

Wait for a clear answer before continuing.

---

## Step 3: Wizard questions

Ask these questions **one at a time** — wait for each answer before asking the next.
After each answer, apply your own knowledge of named services to surface rate limits,
pagination, or auth patterns the user may not know — do not require the user to know
this vocabulary.

1. **Where should the protocol directory live?**
   (Suggest `~/tmp/{task-name}/` if the user has no preference.)

2. **What external APIs or services will this involve?**
   (e.g., Slack, GitHub, Splunk, a database, an internal REST API)
   After the user answers: check your knowledge of each named service for rate limiting,
   pagination, and auth requirements. Surface anything relevant — e.g., "Slack's MCP
   tool has undocumented backoff that escalates under repeated calls; you'll likely need
   a rate limit state file and possibly a CronCreate pattern."

3. **Does any of these services return results in pages, or require a cursor to continue
   where you left off?**
   (Skip if your knowledge of the named service already establishes whether it uses
   pagination — note the answer and move on.)

4. **Is there a known, enumerable list of items to process — or does the scope emerge
   as you go?**
   (e.g., "I have a list of 490 Slack messages" vs. "I'll discover what to process as I read")

5. **Does output accumulate item by item, or is it a single document assembled at the
   end?**
   (e.g., one finding per thread → JSONL accumulator vs. one final report → plain file)

6. **Do you expect some items to fail — deleted resources, permission errors, API errors
   that shouldn't block the rest?**

7. **Do you expect this to span many sessions or days?**

8. **Might the analysis question evolve, or will you need multiple passes over the
   same source data?**
   (e.g., "first categorize, then count patterns, then re-examine a subset" — if so,
   caching raw fetched data locally avoids re-querying a rate-limited API)

9. **Is there a cheap pre-scan you can do before hitting the rate-limited source?**
   (e.g., message previews already cached locally, a metadata file already downloaded,
   or a fast local index to scan before making expensive API calls)
   If yes: structure RESUME.md with an explicit Phase 0 (free scan) before Phase 1 (API
   reads). Phase 0 exhausts what's cheap; Phase 1 only touches items that actually need it.

---

## Step 4: Determine elements

Based on answers, determine which elements to include. Use the Wizard Questions →
Element Mapping table from `protocol-elements.md`. For each row in the table, if the
user's answer implies a 'yes,' include the corresponding element(s). Use judgment where
answers are ambiguous.

Always include:
- `GOAL.md` — MUST always be created. Rationale: without it a resumed session has no stable anchor for what the task is and what success looks like.
- `RESUME.md` — MUST always be created. Rationale: without it every resumed session pays full startup cost re-reading multiple files to reconstruct state.

Conditionally include based on answers:
- Item inventory (`progress.json` or similar) — if items are enumerable
- Results accumulator (`findings.jsonl` or similar) — if output accumulates per item
- Cursor file (`cursor.txt`) — if any service is paginated
- Rate limit state (`rate-limit.json`) — if any service has rate limits
- Error log (`errors.jsonl`) — if partial failure is expected
- Session log (`sessions.log`) — if spanning many sessions
- Reconciliation script — if inventory + accumulator are both present
- Raw data cache (`{source-name}/` subdirectory) — if re-fetching is costly and multiple analysis passes are likely

---

## Step 5: Propose and confirm

Present the proposed directory structure and explain which elements were chosen and why.
For any element the user is unsure about, explain what it prevents (e.g., "without a
rate-limit state file, a resumed session has no way to know whether a backoff is still
in effect").

Ask the user to confirm or adjust before creating anything.

---

## Step 6: Create the directory and files

Create the directory and all confirmed elements. For each file:

**`GOAL.md`** — Write a clear task description based on the conversation. Include:
success criteria, scope (date ranges, target channels/services, what to exclude), and
any constraints the user mentioned.

**`RESUME.md`** — MUST contain a literal first action before handoff. Do not leave this
as a placeholder. Rationale: a RESUME.md that says "start processing" is useless to a
fresh Claude; one that says "run check_progress.py, then call slack_read_thread with the
top pending ts" is immediately actionable. Write it as far as you can given what's known;
the user can refine it before starting.

Structure for RESUME.md:

```markdown
## Task
{one-line description}

## Status
{phase name}: {state} — {evidence, e.g., "490 messages in progress.json"}

## Next Action
{specific, literal instruction — which tool, which file, which item}
```

Include the `## Rate Limit` section only if `rate-limit.json` was created:

```markdown
## Rate Limit
Last call: {not yet started}
Backoff: {0 seconds}
Next call permitted: {any time}
```

**Item inventory** — Create an empty JSON skeleton:
```json
{ "phase": 1, "items": [] }
```
Note in GOAL.md or RESUME.md how to populate it (the first real task step).

**Results accumulator** — Create an empty file. Note the expected record schema in GOAL.md.

**Cursor file** — Create with value `null` or empty.

**Rate limit state** — Create with zeroed values and a `notes` field describing the
service's known behavior based on your knowledge. If you have no documented knowledge
of the service's rate limit behavior, write `notes: 'unknown — update after first
observed limit'` and flag this in the handoff summary.

**Error log** — Create an empty file.

**Session log** — Create an empty file.

**Reconciliation script** — If both inventory and accumulator are present, write a small
Python script (`check_progress.py`) that:
- Reads the completion tracker (not the results accumulator) to get examined item IDs
- Reads the inventory to find pending items
- Prints pending items sorted by a relevant priority field for this task (e.g., severity,
  date, or reply count for message-based tasks)

If using the two-file variant (completion tracker + results accumulator), cross the
inventory against the completion tracker — not the results file. Crossing against results
conflates "no output found" with "not yet examined."

Design the helper script with a CLI argument interface for any writes (see shell injection
gotcha in protocol-elements.md §9). Read-only scripts (status, reconciliation) don't
need this.

---

## Step 7: Handoff summary

Present a summary of how the protocol works end to end:

1. Which elements were created and what each one does in this specific task
2. How sessions hand off to each other (update RESUME.md → cron or manual resume →
   read RESUME.md → continue)
3. The rate limit pattern if applicable (CronCreate at fixed interval, not sleep-retry)
4. If an inventory was created empty, explain how to populate it as the first task step
5. What the user should do to start: review the files, adjust GOAL.md or RESUME.md if
   needed, then begin the first step in RESUME.md

Do NOT start executing the task. Hand off cleanly and wait.
