---
name: notify-me
description: >-
  Send a macOS notification with sound. Use this skill when the user says
  "notify me when done", "notify me when that's done", "let me know when
  finished", "remind me at [time]", "notify me at [time]", "list my
  notifications", "what reminders do I have scheduled", "cancel notification",
  "remove reminder", or any variant asking to be alerted after a task completes
  or at a specific time. Four workflows: immediate (fires after current work),
  scheduled (fires at a clock time), list (shows pending), cancel (removes one).
---

# Notify Me

Send a macOS notification with a sound to alert the user when something completes
or at a specific time. Scheduled notifications use launchd user agents — no sudo
required, survive terminal session closes, and fire on the next wake if the machine
was asleep or off at the scheduled time.

You MUST escape `{MESSAGE}` before shell interpolation — strip or replace any double
quotes, single quotes, and backslashes in the message text. Rationale: failing to do
so breaks `osascript` silently or produces unexpected output.

## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow unless you have a
  specific reason not to; note when you deviate and why.

Every MUST and SHOULD is paired with a rationale. Read it before deciding to deviate.

## Sandbox Requirement

All workflows require `dangerouslyDisableSandbox: true` — `osascript` needs
notification system access, and Workflows 2–4 write to `~/Library/LaunchAgents/`
and call `launchctl`, both outside the sandbox.

## Workflow Routing

| User intent | Workflow |
|---|---|
| "notify me when done", "let me know when finished", alert after a task | Workflow 1 — Immediate |
| "notify me at 2pm", "remind me at [time]", scheduled alert | Workflow 2 — Scheduled |
| "list my notifications", "what reminders do I have" | Workflow 3 — List |
| "cancel that notification", "remove my 2pm reminder" | Workflow 4 — Cancel |

---

## Workflow 1 — Immediate

The user wants a notification after the current task finishes. Do the requested work
first, then fire the notification.

```bash
MSG="{MESSAGE}"  # substitute — strip ", ', \ first
osascript -e "display notification \"$MSG\" with title \"Claude Code\" sound name \"Ping\""
# "Claude Code" — signals task completion initiated by Claude
```

Set `{MESSAGE}` to a one-sentence summary of what just finished. Keep it under 60
characters so it fits in the notification banner without truncation.

Requires sandbox bypass (see above).

---

## Workflow 2 — Scheduled

The user wants a notification at a specific clock time.

### Step 1: Resolve the time and date

Parse the user's time expression (e.g., "1:55pm", "2pm", "14:00") into 24-hour
integer components:

- `{FIRE_HOUR}` — 0–23, no leading zero (used in plist `<integer>`)
- `{FIRE_MINUTE}` — 0–59, no leading zero (used in plist `<integer>`)
- `{FIRE_MONTH}` — 1–12, no leading zero (used in plist `<integer>`)
- `{FIRE_DAY}` — 1–31, no leading zero (used in plist `<integer>`)

Also compute zero-padded two-digit forms for use in the label (Step 2):

- `{FIRE_YEAR}` — 4-digit year
- `{FIRE_MONTH_PAD}` — `{FIRE_MONTH}` zero-padded to 2 digits
- `{FIRE_DAY_PAD}` — `{FIRE_DAY}` zero-padded to 2 digits
- `{FIRE_HOUR_PAD}` — `{FIRE_HOUR}` zero-padded to 2 digits
- `{FIRE_MINUTE_PAD}` — `{FIRE_MINUTE}` zero-padded to 2 digits

Determine the fire date:
- If the time today has not yet passed, use today's date.
- If the time today has already passed, use tomorrow's date and tell the user.

If the time is ambiguous (no am/pm, not inferable from context), ask before
proceeding.

### Step 2: Build the label

The label format is:

    local.claude-notify.{FIRE_YEAR}{FIRE_MONTH_PAD}{FIRE_DAY_PAD}{FIRE_HOUR_PAD}{FIRE_MINUTE_PAD}

Example: `local.claude-notify.202604301430` — 2:30 PM on April 30, 2026.

`{LABEL}` is the full string above with all components substituted. This becomes
both the launchd label and the plist/script filename.

### Step 3: Create and load the job

Before executing this bash block, substitute all `{PLACEHOLDER}` values in the block
text: `{LABEL}` → computed label, `{MESSAGE}` → escaped message text, `{FIRE_MONTH}`
/ `{FIRE_DAY}` / `{FIRE_HOUR}` / `{FIRE_MINUTE}` → resolved integer components (no
leading zeros). These are skill placeholders — the shell will not expand them.

```bash
LABEL="{LABEL}"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
SCRIPT="$HOME/.claude-notify/${LABEL}.sh"

mkdir -p "$HOME/.claude-notify"

# unquoted heredoc: ${LABEL} expands now (write-time); \$HOME and \$0 are escaped to expand at runtime
cat > "$SCRIPT" << SCRIPT_EOF
#!/bin/bash
MSG="{MESSAGE}"  # substitute — strip ", ', \ first
osascript -e "display notification \"\$MSG\" with title \"Reminder\" sound name \"Ping\""
# "Reminder" — signals a user-scheduled alert
launchctl unload "\$HOME/Library/LaunchAgents/${LABEL}.plist"
rm -f "\$HOME/Library/LaunchAgents/${LABEL}.plist" "\$0"
SCRIPT_EOF

chmod +x "$SCRIPT"

# unquoted heredoc: ${LABEL} and ${SCRIPT} expand now (write-time)
cat > "$PLIST" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${SCRIPT}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Month</key>
        <integer>{FIRE_MONTH}</integer>
        <key>Day</key>
        <integer>{FIRE_DAY}</integer>
        <key>Hour</key>
        <integer>{FIRE_HOUR}</integer>
        <key>Minute</key>
        <integer>{FIRE_MINUTE}</integer>
    </dict>
</dict>
</plist>
PLIST_EOF

launchctl load "$PLIST"
```

`${SCRIPT}` and `${LABEL}` are shell variables defined at the top of this bash
block; they expand when each heredoc is processed. The `{FIRE_*}` placeholders must
be substituted manually before executing — they are skill placeholders, not shell
variables.

Requires sandbox bypass (see above).

### Step 4: Confirm

Tell the user the notification is scheduled. Example:
> Scheduled: "Team meeting" at 2:30 PM.

---

## Workflow 3 — List

Show all pending Claude-scheduled notifications.

```bash
shopt -s nullglob
files=("$HOME/Library/LaunchAgents"/local.claude-notify.*.plist)
if [ ${#files[@]} -eq 0 ]; then
  echo "No pending Claude notifications."
else
  for f in "${files[@]}"; do
    base=$(basename "$f" .plist | sed 's/local\.claude-notify\.//')
    y=${base:0:4} mo=${base:4:2} d=${base:6:2} h=${base:8:2} m=${base:10:2}
    # MSG extraction assumes no embedded " — guaranteed by Workflow 2 escaping rule
    msg=$(grep '^MSG=' "$HOME/.claude-notify/$(basename "$f" .plist).sh" 2>/dev/null | head -1 | cut -d'"' -f2)
    printf "%s-%s-%s %s:%s — %s\n" "$y" "$mo" "$d" "$h" "$m" "${msg:-[message unknown]}"
  done
fi
```

Requires sandbox bypass (see above).

Present the output as a numbered list to the user, converting the timestamp to a
readable format (e.g., "April 30, 2026 at 2:30 PM — Team meeting").

---

## Workflow 4 — Cancel

Cancel a pending notification.

If the user identifies one by time (e.g., "cancel my 2:30 notification"), resolve it
to a full label using the format `local.claude-notify.YYYYMMDDHHmm`. If the date is
ambiguous or multiple entries could match, run Workflow 3 first and ask the user to
confirm which one.

```bash
LABEL="{LABEL}"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
SCRIPT="$HOME/.claude-notify/${LABEL}.sh"

launchctl unload "$PLIST" 2>/dev/null
rm -f "$PLIST" "$SCRIPT"
echo "Cancelled: ${LABEL}"
```

Substitute `{LABEL}` with the full label string (including the `local.claude-notify.`
prefix), not just the timestamp component.

Requires sandbox bypass (see above).

Confirm to the user which notification was cancelled and at what time it was scheduled.
