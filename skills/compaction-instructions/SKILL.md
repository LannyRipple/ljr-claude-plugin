---
name: compaction-instructions
description: >-
  Copies /compact summarization instruction to the clipboard so the
  user can paste it immediately after /compact. Trigger when the user types
  /compaction-instructions or asks to get or copy the compaction instructions.
---

# Compaction Instructions

Build a message to provide to /compact.  You are free to re-word but start with:

```
Retain: work intent, decisions made, what was accomplished, any open questions.
Drop: file contents, resolved errors, build logs, tool call details.
```

Add any additional instructions to carry on work that might be currently ongoing.
The context can fill mid-process so compaction won't always be happening at a
nice quiet point between tasks.

If any tmux display panes were opened during this session (via using-tmux or dev-panes),
include a section in the instructions that enumerates each pane — its pane ID (`%N`), what
it was showing (file path, command, workflow type), and the workflow used (billboard,
persistent billboard, show-and-go, etc.).  This allows the post-compaction session to
know what panes exist and what they contain, instead of assuming nothing is open.

Copy the resulting instructions to the clipboard, ready to paste after /compact.
