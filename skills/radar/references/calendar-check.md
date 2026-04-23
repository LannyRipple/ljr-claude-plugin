# Calendar Check Procedure

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

Present as plain text in the agenda under a `CALENDAR` header. Use a fixed-width time
column so event names align. Format each event as:

```
  HH:MM - HH:MM  Event Name
```

For events from the **"Yancey / Ripple"** calendar, append ` (personal)`:
```
  17:00 - 18:00  Rypl-Montrose (personal)
```

Omit meeting links, phone numbers, attendee counts, and descriptions.

If there are no events after filtering, omit the CALENDAR section entirely.

## Example output

```
CALENDAR
  10:00 - 11:00  Claude Code Enablement Session 2
  11:00 - 12:00  AI Cloud Incidents Postmortem | Weekly
  12:30 - 13:00  Backlog Grooming meeting - TDs + WIs as needed
  14:00 - 14:30  PS returning 500 for internal 404
  15:00 - 15:30  RAY Project Sync
  15:30 - 16:00  Lanny / Pradeep - 1:1
  17:00 - 18:00  Rypl-Montrose (personal)
```
