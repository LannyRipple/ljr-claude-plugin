---
name: notify-me
description: >-
  Send a macOS notification with sound. Use this skill when the user says
  "notify me when done", "notify me when that's done", "let me know when
  finished", "remind me at [time]", "notify me at [time]", "list my
  notifications", "what reminders do I have scheduled", "cancel notification",
  "remove reminder", "install notify watchdog", or any variant asking to be
  alerted after a task completes or at a specific time. Five workflows:
  immediate (fires after current work), scheduled (fires at a clock time),
  list (shows pending), cancel (removes one), install watchdog (one-time setup).
---

# Notify Me

Send a macOS notification with a sound to alert the user when something completes
or at a specific time. Scheduled notifications use launchd user agents — no sudo
required, survive terminal session closes, and fire on the next wake if the machine
was asleep or off at the scheduled time.

Notification plists call `/usr/bin/osascript` directly — no bash wrapper — to avoid
macOS background activity prompts per notification. A separate watchdog job (Workflow
5) runs weekly via bash to clean up stale plists; bash registers once at login,
prompting only on first install.

You MUST escape `{MESSAGE}` before use — strip or replace `"`, `'`, `\`, `&`, `<`,
and `>` in the message text. Rationale: double quotes break the AppleScript string;
`&`, `<`, `>` are XML special characters that corrupt the plist.

## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow unless you have a
  specific reason not to; note when you deviate and why.

Every MUST and SHOULD is paired with a rationale. Read it before deciding to deviate.

## Sandbox Requirement

All workflows require `dangerouslyDisableSandbox: true` — `osascript` needs
notification system access, and Workflows 2–5 write to `~/Library/LaunchAgents/`
and call `launchctl`, both outside the sandbox.

## Workflow Routing

| User intent | Workflow |
|---|---|
| "notify me when done", "let me know when finished", alert after a task | Workflow 1 — Immediate |
| "notify me at 2pm", "remind me at [time]", scheduled alert | Workflow 2 — Scheduled |
| "list my notifications", "what reminders do I have" | Workflow 3 — List |
| "cancel that notification", "remove my 2pm reminder" | Workflow 4 — Cancel |
| "install notify watchdog", first-time setup | Workflow 5 — Install Watchdog |

---

## Workflow 1 — Immediate

The user wants a notification after the current task finishes. Do the requested work
first, then fire the notification.

```bash
MSG="{MESSAGE}"  # substitute — strip ", ', \, &, <, > first
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

If the user specifies a relative time (e.g., "in 1 minute", "in 2 minutes") and the
resolved fire time is less than 3 minutes from now, add 2 minutes to the fire time
and tell the user the adjusted time. Rationale: launchd setup takes ~30 seconds and
a tight window risks missing the scheduled minute entirely.

Parse the user's time expression (e.g., "1:55pm", "2pm", "14:00", "in 5 minutes")
into 24-hour integer components:

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
- Relative day expressions ("in 3 days", "next Thursday", "this Friday"): compute
  the target calendar date from today's date, then apply the specified time.
- If no day is specified and the time today has not yet passed, use today's date.
- If no day is specified and the time today has already passed, use tomorrow's date
  and tell the user.

If the time is ambiguous (no am/pm, not inferable from context), ask before
proceeding.

### Step 2: Build the label

The label format is:

    local.claude-notify.{FIRE_YEAR}{FIRE_MONTH_PAD}{FIRE_DAY_PAD}{FIRE_HOUR_PAD}{FIRE_MINUTE_PAD}

Example: `local.claude-notify.202604301430` — 2:30 PM on April 30, 2026.

`{LABEL}` is the full string above with all components substituted. This becomes
both the launchd label and the plist filename.

### Step 3: Create and load the job

Before executing this bash block, substitute all `{PLACEHOLDER}` values: `{LABEL}`
→ computed label, `{MESSAGE}` → escaped message text (strip `"`, `'`, `\`, `&`,
`<`, `>`), `{FIRE_MONTH}` / `{FIRE_DAY}` / `{FIRE_HOUR}` / `{FIRE_MINUTE}` →
resolved integer components (no leading zeros). These are skill placeholders — the
shell will not expand them.

```bash
LABEL="{LABEL}"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

# unquoted heredoc: ${LABEL} expands now (write-time)
cat > "$PLIST" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/osascript</string>
        <string>-e</string>
        <string>display notification "{MESSAGE}" with title "Reminder" sound name "Ping"</string>
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

`${LABEL}` is a shell variable defined at the top of this bash block; it expands
when the heredoc is processed. The `{FIRE_*}` and `{MESSAGE}` placeholders must be
substituted manually before executing — they are skill placeholders, not shell
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
    msg=$(grep 'display notification' "$f" | sed 's/.*display notification "\([^"]*\)".*/\1/')
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

launchctl unload "$PLIST" 2>/dev/null
rm -f "$PLIST"
echo "Cancelled: ${LABEL}"
```

Substitute `{LABEL}` with the full label string (including the `local.claude-notify.`
prefix), not just the timestamp component.

Requires sandbox bypass (see above).

Confirm to the user which notification was cancelled and at what time it was scheduled.

---

## Workflow 5 — Install Watchdog

Install a weekly cleanup job that removes stale notification plists (those whose
scheduled time has passed). This is a one-time setup. The watchdog uses bash and
registers it as a background process once — future weekly runs fire silently without
prompting.

### Step 1: Check if already installed

```bash
launchctl list | grep claude-notify-watchdog && echo "Already installed."
```

If already installed, tell the user and stop. Do not reinstall unless the user
explicitly asks to update it.

### Step 2: Create the watchdog script

```bash
mkdir -p "$HOME/.claude-notify"

cat > "$HOME/.claude-notify/watchdog.sh" << 'WATCHDOG_EOF'
#!/bin/bash
NOW=$(date +%s)
shopt -s nullglob
for plist in "$HOME/Library/LaunchAgents"/local.claude-notify.*.plist; do
    base=$(basename "$plist" .plist | sed 's/local\.claude-notify\.//')
    fire=$(date -j -f "%Y%m%d%H%M" "${base}" +%s 2>/dev/null) || continue
    if [ "$fire" -lt "$NOW" ]; then
        launchctl unload "$plist" 2>/dev/null
        rm -f "$plist"
    fi
done
WATCHDOG_EOF

chmod +x "$HOME/.claude-notify/watchdog.sh"
```

### Step 3: Create and load the watchdog plist

The plist path must contain the user's actual home directory — use the expanded value
of `$HOME` when writing the plist, not the literal string `$HOME`.

```bash
WATCHDOG_PLIST="$HOME/Library/LaunchAgents/local.claude-notify-watchdog.plist"

cat > "$WATCHDOG_PLIST" << WPLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>local.claude-notify-watchdog</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$HOME/.claude-notify/watchdog.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
WPLIST_EOF

launchctl load "$WATCHDOG_PLIST"
```

`$HOME` in the heredoc expands to the actual home directory path at write time
(unquoted delimiter `WPLIST_EOF`). The watchdog fires every Sunday at 3:00 AM and
once immediately on first load to clean up any already-stale plists.

Requires sandbox bypass (see above).

### Step 4: Confirm

Tell the user the watchdog is installed and will run weekly (Sundays at 3 AM).
