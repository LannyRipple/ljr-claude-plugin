# notify-me

Send a macOS notification when a task completes or at a specific time.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/notify-me](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/notify-me).

---

## What This Skill Does

Fires a macOS notification with sound so you can step away while Claude works and
know the moment it's done. Scheduled notifications use launchd user agents — they
survive terminal closes and fire on wake if the machine was asleep.

---

## Workflows

### Notify when done

```
"notify me when done"
"let me know when that's finished"
"notify me when this completes"
```

Fires the notification immediately after the current task finishes.

### Notify at a time

```
"remind me at 3pm"
"notify me at 14:30"
"send a notification in 20 minutes"
```

Schedules a launchd agent to fire at the specified time. Times are interpreted in
your local timezone.

### List pending notifications

```
"list my notifications"
"what reminders do I have scheduled"
"show pending notifications"
```

### Cancel a notification

```
"cancel the 3pm notification"
"remove my reminder"
```

### Install watchdog (one-time setup)

```
"install notify watchdog"
```

Sets up a background process that keeps scheduled notifications alive across session
restarts. Only needed once.

---

## Things Worth Knowing

**Notifications fire even after the terminal closes.** The launchd agent is registered
at the system level, so you don't need to keep a terminal open.

**Fire on wake.** If your Mac is asleep at the scheduled time, the notification fires
when it wakes up — not silently missed.

**Sound included.** Notifications play a sound by default so they're hard to miss when
you're in another app.
