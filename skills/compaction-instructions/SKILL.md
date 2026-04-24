---
name: compaction-instructions
description: >-
  Builds /compact summarization instructions and writes them to a file or copies
  them to the clipboard. Two workflows: "Standard" for the current session, and
  "Compacting a Previous Session" for reviewing a filled session by JSONL.
  Trigger when the user types /compaction-instructions, asks to get or copy the
  compaction instructions, or asks to create compaction instructions for a previous
  or specific session.
---

# Compaction Instructions

## Standard Workflow

Build a message to provide to /compact.  You are free to re-word but start with:

```
Retain: work intent, decisions made, what was accomplished, any open questions.
Drop: file contents, resolved errors, build logs, tool call details.
```

Add any additional instructions to carry on work that might be currently ongoing.
The context can fill mid-process so compaction won't always be happening at a
nice quiet point between tasks. If work was in progress at compaction time, state
the next concrete action explicitly — not just the open question, but the specific
step that should happen first on resume.

Unless otherwise directed copy the resulting instructions to the clipboard, ready
to paste after /compact.

---

## Compacting a Previous Session

Use this workflow when the user has a session whose context filled before compaction
instructions could be written, or when they need to resume a different session.

### Step 1 — Find the session JSONL

If the user provides a session ID, the JSONL is at:

```
~/.claude/projects/{PROJECT_DIR}/{SESSION_ID}.jsonl
```

Where `{PROJECT_DIR}` is the working directory path with `/` replaced by `-`.
For example, `/Users/lripple/ip/claude` becomes `-Users-lripple-ip-claude`.

If the user is running this skill from within the project that filled, find the
most recent session file with:

```bash
ls -lt ~/.claude/projects/$(pwd | sed 's|/|-|g' | sed 's|^-||') | head -5
```

The most recently modified `.jsonl` file (other than the current session) is
the one that filled.  File size can also be used as a verification since a
small file would not have hit the Claude Code context limit.

### Step 2 — Parse the session

Spawn an Explore sub-agent with the prompt template in
`references/summarize-session.md`, substituting the actual JSONL path for
`{JSONL_PATH}`. The agent reads the messages and returns a structured summary
covering:

1. Overall goal / work intent
2. Decisions made
3. What was accomplished
4. Work in progress and next concrete action
5. Open questions and blockers

### Step 3 — Write the compaction instructions

Using the sub-agent's summary, build the compaction instructions following the
same format as the Standard Workflow above (retain/drop header, context
narrative, next concrete action).

Unless otherwise directed copy the resulting instructions to the clipboard, ready
to paste after /compact.
