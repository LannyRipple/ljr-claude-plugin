# Date Check Procedure

Triggered when the user asks to "check the date", "what day is it", or any phrasing that
clearly means the same thing in context.

## Steps

1. Run `date` via Bash to get today's date.
2. Read `last-date-check` from the frontmatter of `$HOME/tmp/radar-memory.md`.
3. Compare the two dates.

---

### If more than one day has passed

Read through all entries. Identify items to flag for cleanup discussion.

**Flag immediately (older than 2 weeks):**
- Open TODOs (`- [ ] ...`) — if it hasn't been touched in 2 weeks, it's either done,
  abandoned, or needs a nudge
- Appointments with a past date
- Reminders that appear time-bounded

Present these as a list and ask what to do with each. Wait for the user's direction
before making any changes.

**Flag on judgment (no hard age cutoff):**
- Notes that clearly refer to a resolved or past situation
- Reminders about things that no longer seem live given other context in the file
- Completed todos (`- [x] ...`) that have piled up — offer to remove or archive them

The judgment call is: would a competent aide still keep this on the desk, or would they
have filed it away? When in doubt, ask rather than delete.

**Do not flag:**
- Standing reference notes (people's contact info, team context, project background)
- Recurring reminders that are clearly ongoing
- Anything that's visibly still active

The goal is to keep the file lean and useful. Notes that never get pruned turn into noise,
and Radar is only as useful as the quality of what's in memory.

### If less than one day has passed

Confirm the date briefly and move on. No review needed.

---

## After the check

Update `last-date-check` to today in the frontmatter, regardless of whether anything
was flagged or changed.

## Connecting the date to near-future context

After confirming the date, quickly scan for entries relevant to today or the next few days —
upcoming appointments, reminders that are due soon. Surface these without being asked:
> *"By the way, you have that MLS team sync tomorrow morning."*

This is the anticipatory piece. The date check is a good natural trigger for it.

## Recurring reminder intervals

Reminders with an interval label should only be surfaced when that interval has actually
elapsed — not simply because the entry exists in the file.

**Interval-based** (compare elapsed days since entry date):
- **Daily** — surface every time the date has advanced by at least 1 day
- **Weekly** — surface only when 7+ days have passed since the entry date
- **Bi-weekly** — surface only when 14+ days have passed since the entry date

When surfacing an interval-based reminder, update its date to today so the interval resets.

**Day-of-week** (e.g., "Mon/Wed/Fri:", "Tuesday:"):
- Surface only when today matches one of the specified days
- Run `date +%A` via Bash to get the current day name if not already known
- Do not update the entry date — the original date is just a record of when the reminder
  was created, not a firing timestamp

Do not surface a recurring reminder that isn't due just because it's visible in the file.
