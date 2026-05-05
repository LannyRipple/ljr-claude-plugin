# hooks

Automated behaviors that fire on Claude Code lifecycle events.

For a full understanding, read the hook files in
[ljr-claude-plugin/hooks](https://github.com/lripple/ljr-claude-plugin/tree/main/hooks).

---

## precompact-auto

Fires on automatic compaction. Intercepts the compaction, generates tailored
instructions, and hands control back to you for a manual `/compact` run.

**What it does:**
1. Reads the session transcript
2. Calls the Claude API to generate structured compaction instructions (retain/drop
   header + `### User Intent`, `### Completed Work`, etc.)
3. Writes instructions to a temp file and copies to clipboard
4. Exits with `continue: false` to halt the auto-compaction

**Why halt auto-compaction?** Auto-compaction uses a generic summary. The hook generates
a summary tailored to the session's actual content — work intent, decisions, open
questions — and puts it on your clipboard so you can run `/compact [paste]` immediately.

**After the hook fires:**
```
/compact [paste from clipboard]
```

The `compaction-instructions` skill does the same thing on demand, without waiting for
auto-compaction to trigger.

---

## Things Worth Knowing

**Requires an Anthropic API key.** The hook calls the Claude API directly — it uses the
`ANTHROPIC_API_KEY` environment variable. If the key isn't set, the hook exits cleanly
and auto-compaction proceeds normally.

**The hook fires on auto-compaction only.** Manual `/compact` is not intercepted. If
you want tailored instructions for a manual compact, use `/compaction-instructions`.
