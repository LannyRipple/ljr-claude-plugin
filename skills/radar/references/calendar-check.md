# Calendar Check Procedure

<!-- NOT LINKED: Removed from SKILL.md pending better calendar tooling. The blocking
     gap is per-attendee RSVP visibility — without knowing whether Lanny specifically
     accepted/declined/tentatively accepted, status defaults to "new" for everything,
     which isn't worth the tokens. Re-link when the calendar API exposes the invite
     list with individual yes/no/maybe status. -->


Run this during agenda building. Use `mcp__plugin_google_google__calendar_events` to
fetch today's events across all calendars.

## Fetch

```
calendar_events(start_date=TODAY, end_date=TODAY, calendars="all")
```

## Filtering

- **Discard** any event where the user's RSVP status is declined.
- **Discard** all-day events that are not personal appointments (e.g. PTO markers for
  other people, OOO blocks for teammates).

## Formatting

Present as plain text in the agenda under a `CALENDAR` header. Use fixed-width columns:

```
  HH:MM - HH:MM  STATUS  Event Name
```

The STATUS column is 6 characters wide and uses these values:

| Status | When to use |
|--------|-------------|
| `yes   ` | User accepted the invite |
| `maybe ` | User tentatively accepted |
| `new   ` | No response yet (pending) |
| `-team-` | Event is from the **Einstein ML Services** calendar (OOO/PTO/team awareness) |
| `-Y/R- ` | Event is from the **Yancey / Ripple** personal calendar |
| `-     ` | Catch-all: any other all-day or non-invite event with no RSVP context |

List all-day events first (as Google Calendar does), then timed events in chronological
order. Omit meeting links, phone numbers, attendee counts, and descriptions.

If there are no events after filtering, omit the CALENDAR section entirely.

## Example output

```
CALENDAR
  all day        -team-  Anusha PTO
  all day        -Y/R-   Rypl-Montrose
  10:00 - 11:00  yes     Claude Code Enablement Session 2
  11:00 - 12:00  new     AI Cloud Incidents Postmortem | Weekly
  12:30 - 13:00  maybe   Backlog Grooming meeting - TDs + WIs as needed
  14:00 - 14:30  yes     PS returning 500 for internal 404
  15:00 - 15:30  new     RAY Project Sync
  15:30 - 16:00  yes     Lanny / Pradeep - 1:1
```
