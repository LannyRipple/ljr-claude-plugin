# Meeting Notifiers

This procedure runs during agenda building, between the calendar fetch and the
show-and-go display.

## Step 1: Post the calendar in chat

After fetching calendar events (see `calendar-check.md`), post the full event list
in chat using the same STATUS column format. Include all non-declined events:
`-team-`, `-Y/R-`, `-`, `yes`, `maybe`, and `new`.

Do NOT open the show-and-go pane yet. Wait for the user to respond.

## Step 2: Ask which meetings need notifiers

Ask once, concisely:

> Which of these do you want 5-minute notifications for?

Wait for the user's response. They will reply with times or event names. Examples:
- "the 10am and 2:30" → notify both, status `yes`
- "3pm is a maybe" / "I might go to the 5:30" → notify, status `maybe`
- No mention of an event → treat as declined, omit from show-and-go

## Step 3: Schedule notifications

For each claimed meeting, schedule a notify-me notification 5 minutes before the
start time using `launchctl` (Workflow 2 of the notify-me skill).

**Message format:** `"Starting in 5: {EVENT_NAME}"`

Truncation: the full message MUST be ≤ 60 characters. The prefix "Starting in 5: "
is 15 characters, leaving 45 for the event name. If the event name exceeds 45
characters, truncate it and append `...`.

**Timing:** Subtract 5 minutes from the event start time to get the fire time. If
the resulting fire time is less than 3 minutes from now, warn the user and ask
whether to skip it or schedule anyway.

Schedule all notifications in one pass — do not ask for per-meeting confirmation.
After scheduling, briefly confirm:

> Notifiers set: 9:55 AM (Team Sync), 1:55 PM (1:1 with Pradeep)

## Step 4: Build the show-and-go content

Construct the agenda content for the show-and-go pane. The CALENDAR section MUST
include only:

- All-day events (any status: `-team-`, `-Y/R-`, `-`) → always include
- Timed `-Y/R-` events (non-work personal/family calendar) → always include
- Timed work events the user claimed for a notifier → show as `yes` or `maybe`
- Timed work events the user did NOT claim → omit entirely

This means the show-and-go reflects the day as committed: team/family context and
the work meetings Lanny is actually attending. Unclaimed work meetings do not appear.

Proceed to open the show-and-go pane (see Agenda Display in SKILL.md). Do not wait
for the user to close it.
