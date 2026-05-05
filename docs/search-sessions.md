# search-sessions

Search old Claude Code session transcripts by keyword.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/search-sessions](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/search-sessions).

---

## What This Skill Does

Searches through session transcript `.jsonl` files under `~/.claude/projects/` for
one or more keywords. Returns matching sessions with: session ID, project directory,
timestamps, first user message, and up to 3 in-context snippets where the keyword
appears — plus a resume command so you can jump back into a matching session.

By default searches the project matching the current working directory. Ask to search
"everywhere" or "across all projects" to widen the scope.

---

## Usage

```
/search-sessions slack rate limit
/search-sessions CronCreate backoff
/search-sessions prediction service auth — search everywhere
```

The keywords are passed directly as the argument — no quotes needed.

---

## Things Worth Knowing

**Searches message content only.** Tool call inputs/outputs and system messages are
excluded — matches are against what you and Claude actually said.

**Fast.** Uses `grep` for initial file matching, then Python to parse and extract
context. Only opens files that contain the keyword.

**Resume commands are included.** Each result shows a `claude --resume <session-id>`
command you can run to pick up that session.
