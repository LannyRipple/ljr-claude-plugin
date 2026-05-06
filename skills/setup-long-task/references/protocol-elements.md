# Protocol Elements for Long-Running Tasks

A long-running task is one that spans multiple Claude sessions, compaction boundaries,
or rate-limited APIs. This reference covers the building blocks of a resumable protocol
and when each one is needed.

---

## Element Catalog

### 1. `GOAL.md` — Task description (always)

What the task is, what success looks like, scope, and constraints. Written once by the
wizard during setup. Never updated during execution — it is the stable anchor.

**Contents:** plain prose. Problem statement, success criteria, any known constraints
(date ranges, target channels/repos/services, what to exclude).

---

### 2. `RESUME.md` — Re-entry point (always)

The single file a fresh Claude reads to orient and begin working. Must be written in
imperative terms that require no prior context to follow.

**Contents:**
- Current step name and phase
- What has been verified complete
- **Next Action** — a specific, literal instruction: which tool to call, with which
  arguments, on which file or item. Not "continue processing" but
  "call `slack_read_thread` with `ts=1773163973.519889`, append result to `findings.jsonl`."
- Active constraints (rate limit policy, backoff in effect, etc.)

**Maintenance:** Updated at every checkpoint — before stopping, before a rate-limit wait,
after each phase boundary. This is the most important file in the protocol.

---

### 3. Item inventory — Work queue (when items are enumerable)

Needed when the task has a known, enumerable set of items to process (messages, files,
tickets, rows). Provides the full list with metadata so any session can determine what
remains.

**Format:** JSON — an object with a top-level array. Each item has at minimum:
```json
{ "item_id": "...", "status": "pending|done|error", "metadata": {} }
```
The key name should match the natural identifier for the data source (e.g., `ts` for
Slack messages, `number` for GitHub issues).

**Two approaches:**

*Mutable inventory* — update `status` in place as items complete. Simple, but risks
partial writes if compaction fires mid-update.

*Append-only reconciliation* (recommended for large inventories) — inventory is read-only
after initial population; completion is tracked by appending to a results accumulator.
A small reconciliation script crosses the two to show pending vs. done. Safer across
compaction; the Slack case study used this pattern.

---

### 4. Results accumulator — Output store (when output accumulates)

Needed when output builds item by item across many sessions. Append-only: each completed
item adds one record. Never requires editing existing content.

**Format:** JSONL (one JSON object per line). Each record should include enough context
to be useful standalone: item ID, timestamp, key output fields.

**When not needed:** If the task produces a single document assembled at the end (a
report, a summary), a plain output file is fine. The accumulator pattern is for tasks
where "done so far" is meaningful independently of "done entirely."

**Two-file variant (when most items produce no output):** If only a fraction of items
produce a result record (e.g., scanning 460 messages to find 26 referrals), use a
separate completion tracker alongside the results accumulator:

- `checked.jsonl` — one entry per examined item, whether or not it produced output.
  The reconciliation script crosses the inventory against this file to show progress.
- `results.jsonl` — only items that produced output.

Do not cross the inventory against `results.jsonl` for progress: that conflates "nothing
found" with "not yet examined." Without a completion tracker, a resumed session cannot
distinguish the two.

**Completion detection — specify the format upfront:** The reconciliation script must
have an unambiguous rule for what counts as "done." Define it explicitly in GOAL.md or
in the script itself — which field and which value/prefix mark an item complete. If the
format drifts across sessions (e.g., note field uses different prefixes), items will be
silently miscounted. Decide once and enforce it in the helper script.

---

### 5. Cursor / pagination state — Position tracker (when data is paginated)

Needed when the data source is paginated or cursor-based (Slack channel history, GitHub
issue list, database offset, date window). The cursor lets any session pick up exactly
where the last one left off.

**Format:** plain text file (`cursor.txt`), one value. Updated immediately after fetching
each page and before processing its results — so a crash during processing doesn't advance
the cursor past unsaved data.

**Also record:** the total expected item count if the API provides it, so RESUME.md can
show progress as "X of N."

---

### 6. Rate limit state — Backoff tracker (when calling rate-limited APIs)

Needed when an external API has rate limits, especially for tasks spanning multiple
sessions. A fresh Claude has no way to know how much of a backoff remains without this.

**Format:**
```json
{
  "last_call_ts": "2026-04-10T14:32:00Z",
  "backoff_seconds": 1200,
  "calls_this_window": 3,
  "notes": "Slack MCP: backoff escalates under repeated calls; reset is slow"
}
```

**Maintenance:** Updated after every API call. RESUME.md should reference this file and
instruct the resuming Claude to check it before making any calls.

**Rate limit pattern:** When backoff periods are long (minutes), do not have Claude
sleep and retry — this ties up context and fails across compaction. Instead, use
`CronCreate` to schedule the next call at a fixed interval. Claude exits; the cron
tick fetches one page, appends results, updates cursor and rate-limit state, then exits
again. See the case study below for a worked example.

---

### 7. Error log — Failure record (when partial failure is expected)

Needed when some items are expected to fail (deleted resources, permission errors, API
errors) and those failures need to be tracked separately from "not yet processed."

**Format:** JSONL. Each record:
```json
{ "ts": "...", "item_id": "...", "error_type": "transient|permanent", "message": "...", "attempt": 1 }
```

Transient errors (rate limit, timeout) may be retried. Permanent errors (deleted,
forbidden) should be skipped on resume and noted in the final output.

---

### 8. Session log — Execution history (when multiple compaction cycles are expected)

Needed for tasks spanning many sessions. Helps diagnose state inconsistencies ("why does
the progress file say X but the data looks like Y?").

**Format:** append-only plain text or JSONL. Each entry: timestamp, items processed,
errors encountered, notes.

```
2026-04-10T14:30Z  Processed 12 threads (ts range 1773..–1775..). 2 errors (permanent). Cursor: dXNlc...
2026-04-10T15:30Z  Processed 8 threads. Rate limit hit at item 6; CronCreate scheduled for 15:50Z.
```

---

### 9. Helper scripts — Reconciliation and status tools (when complexity warrants)

Small Python or shell scripts that answer "where are we?" without requiring Claude to
read and reason over multiple files.

**Most useful:** a reconciliation script that crosses the inventory against the
accumulator and prints pending items sorted by priority (e.g., by reply count, by
severity). On resume, running this script gives an instant status without token cost.

**When not needed:** simple tasks with a single linear sequence don't need a script —
RESUME.md is sufficient.

**Shell injection gotcha — use named-arg CLI scripts for state writes:** Claude Code's
built-in shell injection check blocks Python dict literals (`{'key': value}`) inside
bash heredocs, regardless of the heredoc delimiter style. This fires whenever a helper
script needs to write JSON state (rate-limit.json, checked.jsonl, results.jsonl) from
within a bash command. The workaround: extract all logic that uses dict literals into a
`.py` file and call it with named CLI arguments:

```bash
python3 bookkeep.py --ts 1234567890 --no-result
python3 bookkeep.py --ts 1234567890 --result --category "Auth" --referred-to "some-team"
```

Design helper scripts with a CLI argument interface from the start. Scripts that only
read and print (reconciliation, status) are fine as heredocs.

---

### 10. Raw data cache — Fetched source material (when re-fetching is costly)

Needed when fetching raw data from an external source is expensive (rate-limited, slow,
or requires auth) and the task may require multiple passes over the same data — e.g.,
a first pass to categorize, a second to count patterns, a third after the user refines
the analysis question.

**Format:** a subdirectory (e.g., `threads/`, `issues/`, `pages/`) containing one file
per fetched item. File format matches what the API returns: JSON, text, or structured
records. Naming convention: `{item_id}.json` or `{ts}.json`.

**The pattern:** fetch once, analyze many times. Store the raw API response as-is so
any future analysis can re-read without re-querying. This decouples the fetch phase
(rate-limited, stateful) from the analysis phase (cheap, repeatable).

**When not needed:** if the task is a single linear pass with no likelihood of revisiting
raw data, the overhead of maintaining the cache isn't worth it. Use judgment: if the
data source is rate-limited and the analysis question might evolve, cache it.

---

## Wizard Questions → Element Mapping

The setup wizard asks these questions to determine which elements to include:

| Question | Elements it determines |
|---|---|
| What external APIs or services will this involve? | Rate limit state (6) — if service is rate-limited; cursor (5) — if service is paginated |
| Does the API/service have pagination or cursor-based navigation? | Cursor (5) |
| Is there a known list of items to process, or is scope discovered as you go? | Item inventory (3) |
| Does output accumulate item by item, or is it a single document at the end? | Results accumulator (4); two-file variant (4) if most items produce no output |
| Do you expect some items to fail (deleted, forbidden, API errors)? | Error log (7) |
| Do you expect this to span many sessions or days? | Session log (8), helper scripts (9) |
| Might the analysis question evolve, or will you need multiple passes over the same data? | Raw data cache (10) |
| Is there a cheap pre-scan you can do before hitting the rate-limited source? | Phase structure in RESUME.md — see below |

Elements 1 (GOAL.md) and 2 (RESUME.md) are always included.

**Cheap pre-scan phase:** If some signal can be extracted from already-available data
(cached files, local copies, message previews) before making any rate-limited API calls,
structure the task into explicit phases: Phase 0 (free scan, no API calls) → Phase 1
(API reads for items that need it). Phase 0 exhausts what's cheap before touching the
rate-limited source. The RESUME.md phase structure should name these phases explicitly
and track which phase is active. This often reduces the number of API calls substantially.

---

## Case Study: Slack Channel Analysis (6 months, rate-limited)

**Task:** Analyze 6 months of a support channel (#agentforce-foundations-prediction-svc),
reading thread replies to categorize incidents and extract structured findings.
490 messages, ~120 with threads. Produce a report.

**Why this was hard:**
- Too many items to process in one session — multiple compaction boundaries guaranteed
- Slack MCP has undocumented rate limiting with linear/exponential backoff and slow cooldown.
  Initial 30-second backoff grew under repeated calls. Attempts to stay within limits
  by waiting 30s, then 60s, kept escalating. Eventually settled on 20-minute fixed
  intervals driven by `CronCreate` rather than having Claude manage the timing.
- Result: ~10 sessions over several hours to process 40 high-reply threads

**Elements used and their roles:**

| File | Element | Role |
|---|---|---|
| `progress.json` | Item inventory (3) | 490 messages with ts, reply_count, preview, sender, status |
| `findings.jsonl` | Results accumulator (4) | One record per analyzed thread — category, summary, resolution, severity |
| `threads/` | Raw data cache (10) | One JSON file per fetched thread (named by ts). Allowed re-analysis without re-querying Slack |
| `check_progress.py` | Helper script (9) | Cross-references inventory vs. findings; prints pending threads sorted by reply count |
| `phase1_scan.py`, `parse_batch.py` | Helper scripts (9) | Parsing helpers for Slack batch API responses |
| `report.md` | Final output | Assembled at end from findings.jsonl |

**Elements not used that would have helped:**

- **`RESUME.md`** — absent. Each session required reading `progress.json`, running
  `check_progress.py`, and reasoning about state. A RESUME.md with a literal next action
  would have eliminated this startup cost entirely.
- **Rate limit state file** — absent. The 20-minute backoff rule had to be re-stated
  every session. A `rate-limit.json` with `last_call_ts` and `backoff_seconds` would
  have let the resuming Claude check immediately whether a wait was still in effect.
- **Session log** — absent. No record of when each session ran or how many items it
  processed. This made it hard to diagnose why the progress file and findings count
  occasionally diverged.

**The reconciliation pattern:**

`progress.json` was never mutated after initial population. As threads were analyzed,
records were appended to `findings.jsonl`. `check_progress.py` crossed the two files:

```python
done_ts = {json.loads(line)['ts'] for line in open('findings.jsonl') if line.strip()}
pending = [m for m in progress['messages'] if m['ts'] not in done_ts and m.get('reply_count', 0) > 0]
pending.sort(key=lambda x: x['reply_count'], reverse=True)
```

This was safe across compaction: appending to JSONL never risks a partial write corrupting
the inventory. The cost was the extra script; the benefit was zero inventory corruption
across 10 sessions.

**The rate limit pattern:**

Rather than having Claude sleep and retry (which fails silently across compaction), each
session ended with a `CronCreate` call:

```
Use /resume-long-task with path ~/tmp/prediction-svc-report/ — or instruct the cron tick
to read RESUME.md and execute its Next Action directly.
```

Each cron tick: fetch one Slack thread, append to findings.jsonl, update RESUME.md with
the next pending ts, exit. Claude is idle between ticks. Compaction during a 20-minute
wait is harmless because RESUME.md carries the exact next action.

**What a RESUME.md would have looked like:**

```markdown
## Task
Analyze Slack channel C015DEF50TX support threads Nov 2025–Apr 2026.

## Status
Phase 1 (channel scan): complete — 490 messages in progress.json
Phase 2 (thread analysis): in progress — 31 of 120 threaded messages analyzed

## Rate Limit
Last Slack MCP call: 2026-04-10T14:32Z
Backoff: 1200 seconds (20 minutes)
Next call permitted after: 2026-04-10T14:52Z

## Next Action
Check rate limit above. If wait has elapsed:
  Run check_progress.py to get current top pending thread.
  Call slack_read_thread with ts=1773163973.519889 (77 replies — top pending).
  Append finding to findings.jsonl.
  Update this file: new Next Action ts, updated last call time.
If wait has not elapsed:
  CronCreate: resume in {remaining} minutes, read this file and continue.
```
