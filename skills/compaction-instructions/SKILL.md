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

Then write a structured summary using these sections (### headers, omit sections with nothing to say):

```
### User Intent
What the user was trying to accomplish overall.

### Completed Work
What was finished. Include exact file paths, symbol names, and identifiers.

### Errors & Corrections
Mistakes made and how resolved. User corrections verbatim.

### Active Work
What was in progress when compaction triggered.

### Pending Tasks
Outstanding items not yet started.

### Key References
File paths, config values, identifiers, and constraints a resumed session needs.
```

Preserve always: exact file paths, symbol names, error messages verbatim, user corrections,
specific config values, technical constraints.

Compression rules: weight recent messages more heavily; omit pleasantries, exploratory dead
ends, and resolved errors already captured above; keep each section under 500 words; cut
filler before cutting facts.

The context can fill mid-process so compaction won't always be happening at a nice quiet
point between tasks. If work was in progress at compaction time, end with a `Next action:`
line stating the specific next step — not a vague goal, but the concrete first action on resume.

Write the instructions to /tmp/claude-502/compaction-instructions.md and then
copy them to the clipboard with `cat /tmp/claude-502/compaction-instructions.md | pbcopy`.

---

## Ensure Auto-Compact Instructions in User CLAUDE.md

After writing the compaction instructions, check whether `~/.claude/CLAUDE.md` contains
an `# Auto-Compact Instructions` section.

```bash
grep -q "^# Auto-Compact Instructions" ~/.claude/CLAUDE.md && echo "EXISTS" || echo "MISSING"
```

**If MISSING:** Append the following block to `~/.claude/CLAUDE.md`:

```
# Auto-Compact Instructions

When auto-compaction fires, write a structured summary using these sections
(### headers; omit sections with nothing to say):

Retain: work intent, decisions made, what was accomplished, any open questions.
Drop: file contents, resolved errors, build logs, tool call details.

### User Intent
What the user was trying to accomplish overall.

### Completed Work
What was finished. Include exact file paths, symbol names, and identifiers.

### Errors & Corrections
Mistakes made and how resolved. User corrections verbatim.

### Active Work
What was in progress when compaction triggered.

### Pending Tasks
Outstanding items not yet started.

### Key References
File paths, config values, identifiers, and constraints a resumed session needs.

Preserve always: exact file paths, symbol names, error messages verbatim, user corrections,
specific config values, technical constraints.

Compression rules: weight recent messages more heavily; omit pleasantries, exploratory dead
ends, and resolved errors already captured above; keep each section under 500 words;
cut filler before cutting facts.

If work was in progress when compaction triggered, end with a `Next action:` line
stating the specific next step — not a vague goal, but the concrete first action on resume.
```

Tell the user the section was added.

**If EXISTS:** Tell the user the section already exists and ask if it should be updated
to match the current structured format. Do not update it unless the user says yes.

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
`${CLAUDE_SKILL_DIR}/references/summarize-session.md`, substituting the actual JSONL path for
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

Write the instructions to /tmp/claude-502/compaction-instructions.md and then
copy them to the clipboard with `cat /tmp/claude-502/compaction-instructions.md | pbcopy`.
