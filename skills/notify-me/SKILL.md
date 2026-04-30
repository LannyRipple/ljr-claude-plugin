---
name: notify-me
description: >-
  Send a macOS notification with sound. Use this skill when the user says
  "notify me when done", "notify me when that's done", "let me know when
  finished", "remind me at [time]", "notify me at [time]", or any variant
  asking to be alerted after a task completes or at a specific time.
  Two workflows: immediate (fires after current work completes) and
  scheduled (fires at a clock time the user specifies).
---

# Notify Me

Send a macOS notification with a sound to alert the user when something completes
or at a specific time.

You MUST escape `{MESSAGE}` before shell interpolation — strip or replace any double
quotes and backslashes in the message text. Failing to do so breaks the `osascript`
command silently or produces unexpected output.

## Workflow Routing

| User intent | Workflow |
|---|---|
| "notify me when done", "let me know when finished", alert after a task | Workflow 1 — Immediate |
| "notify me at 2pm", "remind me at [time]", scheduled alert | Workflow 2 — Scheduled |

---

## Workflow 1 — Immediate

The user wants a notification after the current task finishes. Do the requested work
first, then fire the notification.

```bash
MSG="{MESSAGE}"
osascript -e "display notification \"$MSG\" with title \"Claude Code\" sound name \"Ping\""
```

Set `{MESSAGE}` to a one-sentence summary of what just finished. Keep it under 60
characters so it fits in the notification banner without truncation.

Requires `dangerouslyDisableSandbox: true`.

---

## Workflow 2 — Scheduled

The user wants a notification at a specific clock time.

### Step 1: Resolve the time

Parse the user's time expression (e.g., "1:55pm", "2pm", "14:00") into `HH:MM` 24-hour
format. If the time is ambiguous (no am/pm and not obvious from context), ask for
clarification before proceeding.

### Step 2: Ensure atd is running

`atd` is disabled by default on macOS and requires `sudo` — Claude cannot run it directly.
If it may not be running, tell the user you need them to enable atd, then send a second
response containing ONLY the command and nothing else — no prose, no code fences, no
explanation — so `/copy` captures exactly the command:

    sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist

Prefix the command with a shell comment explaining what it does, so the user knows
what they're pasting. Example output:

    # Enable atd (one-time per boot, required for scheduled notifications)
    sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist

Wait for the user to confirm before proceeding. This is a one-time setup per boot — if
the user has already confirmed it this session, skip this step.

### Step 3: Schedule with `at`

```bash
MSG="{MESSAGE}"
echo "osascript -e \"display notification \\\"$MSG\\\" with title \\\"Reminder\\\" sound name \\\"Ping\\\"\"" | at {HH:MM}
```

Set `{MESSAGE}` to the user's reminder text verbatim (or a close paraphrase if it was
conversational).

Requires `dangerouslyDisableSandbox: true`.

`at` fires once at the scheduled time and survives terminal session closes. It does not
persist across reboots — if the machine restarts before the scheduled time, the job is
lost. For anything that needs to survive a reboot, set a phone alarm or calendar event
directly.

**Fallback — if `at` is unavailable:** Use a background sleep instead:

```bash
MSG="{MESSAGE}"
SECONDS=$(( $(date -j -f "%H:%M" "{HH:MM}:00" +%s) - $(date +%s) ))
(sleep $SECONDS && osascript -e "display notification \"$MSG\" with title \"Reminder\" sound name \"Ping\"") &
```

This fires within the current session only.

### Step 4: Confirm

Tell the user the notification is scheduled and at what time. Example:
> Scheduled: "Team meeting" notification at 1:55 PM.
