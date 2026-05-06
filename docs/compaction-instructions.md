# compaction-instructions

Builds tailored `/compact` instructions for the current session and puts them on the
clipboard.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/compaction-instructions](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/compaction-instructions).

---

## The Core Idea

Claude Code's `/compact` command summarizes the session to free up context, but by
default it uses a generic summary. This skill generates instructions that tell `/compact`
exactly what to retain (work intent, decisions, open questions) and what to drop (file
contents, resolved errors, build logs). The result is a compaction that preserves the
things you actually need to continue working while shedding the bulk.

See also: the `precompact-auto` hook, which fires this automatically on auto-compaction
so you don't have to think about it.

---

## Workflows

### Standard — current session

Generates compaction instructions for the session you're in right now.

```
/compaction-instructions
"get the compaction instructions"
"copy compaction instructions to clipboard"
```

The skill writes the instructions to a temp file and copies them to the clipboard. You
then run `/compact` and paste.

### Compacting a previous session

Reviews a previous session's JSONL transcript and generates instructions for it.

```
/compaction-instructions — session abc123
"compaction instructions for the previous session"
```

---

## Things Worth Knowing

**The `precompact-auto` hook does this automatically.** When auto-compaction triggers,
the hook calls the Claude API directly, generates instructions, copies them to the
clipboard, and then lets auto-compaction proceed. You don't need to invoke this skill
manually unless you want to review or tweak the instructions before compacting.

**Instructions follow a fixed structure.** The retain/drop header is always verbatim;
the structured sections (`### User Intent`, `### Completed Work`, etc.) are generated
from session content. Omit sections with nothing to say — don't pad with empty headers.
