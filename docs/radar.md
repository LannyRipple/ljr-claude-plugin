# radar

A personal assistant named after Corporal Radar O'Reilly from MASH. Keeps notes,
tracks todos, and recalls things you've mentioned across sessions.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/radar](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/radar).

---

## The Core Idea

Radar maintains a persistent memory file (`~/tmp/radar-memory.md`) that survives
session resets and compactions. Anything you ask Radar to remember, track, or note
ends up there. When you need it back, Radar reads the file and reports.

Trigger by addressing Radar by name. Once invoked in a session, subsequent note and
todo requests are treated as Radar tasks without re-invoking the name.

---

## Operations

### Save a note

```
"Hey Radar, remember that the Slack backoff resets after 20 minutes"
"Radar, note: perf2 is reserved until Friday"
"Radar, jot down that we decided to use CronCreate for rate-limited tasks"
```

### Track a todo

```
"Radar, add 'follow up on the FI schedule cleanup' to my todos"
"Radar, remind me to check the auth migration status tomorrow"
```

### Recall

```
"Radar, what did I say about the Slack rate limit?"
"Radar, what's on my todo list?"
"Radar, what do you know about the oncall report?"
```

### Clear or update

```
"Radar, mark the FI schedule cleanup as done"
"Radar, remove the perf2 note"
```

---

## Things Worth Knowing

**One file, append-friendly.** The memory file is plain markdown — easy to read and
edit directly if you want to manage it outside of Claude.

**Persists across compaction.** Session compaction drops conversation context but
the memory file is on disk. Radar will re-read it fresh in any new session.

**Don't trigger on the word "radar".** The skill only activates when you're addressing
Radar as an assistant — not when the word appears in a technical context (weather radar,
detection systems, the RADAR acronym).
