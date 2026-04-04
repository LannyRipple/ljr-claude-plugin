# Memory Report Procedure

Triggered when the user asks for a "memory report", "overview of what you're tracking",
"what's in your memory", "show me what you have on file", or any equivalent phrasing.

## Steps

1. Run `date` via Bash to get today's date.
2. Read `$HOME/tmp/radar-memory.md`.
3. Parse each section and produce the report below.

---

## Report Format

```
Memory Report — YYYY-MM-DD

Section       Entries   Detail
-----------   -------   ------
TODO          N         X open, Y completed  |  oldest open: YYYY-MM-DD
Appointments  N                              |  oldest: YYYY-MM-DD
Reminders     N                              |  oldest: YYYY-MM-DD
Notes         N                              |  oldest: YYYY-MM-DD
[other]       N                              |  oldest: YYYY-MM-DD

[stale callout if any]
[upcoming callout if any]
```

Omit sections that have zero entries. Omit the callouts if nothing qualifies.

### TODO detail

Count entries with `- [ ]` as open and `- [x]` as completed. Report both.
"Oldest open" is the earliest date stamp on a `- [ ]` entry.

### Oldest entry

For non-TODO sections, oldest is simply the earliest date stamp in the section.
If a section has no date stamps, note it as "no dates".

### Stale callout

Use the same 2-week threshold from `references/date-check.md`. Count:
- Open TODOs older than 2 weeks
- Time-bounded reminders older than 2 weeks
- Past appointments

If any exist, append one line:
> Stale: N items older than 2 weeks — run a date check to review.

### Upcoming callout

Scan for entries with a date in the next 7 days. If any exist, append one line:
> Upcoming (next 7 days): [brief list — e.g., "1 appointment Thu, 2 reminders"]

---

## Notes

- This report is read-only. Do not modify the memory file.
- If the file doesn't exist, say so and offer to initialize it.
- Keep the report concise — it's an orientation, not a full dump. The user can ask
  to recall specifics from any section afterward.
