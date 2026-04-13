---
name: compaction-template
description: >-
  Copies the standard /compact summarization template to the clipboard so the
  user can paste it immediately after /compact. Trigger when the user types
  /compaction-template or asks to get or copy the compaction template.
---

# Compaction Template

Run the following command with `dangerouslyDisableSandbox: true` set on the Bash tool call:

```bash
echo -n "Retain: work intent, decisions made, what was accomplished, any open questions. Drop: file contents, resolved errors, build logs, tool call details." | pbcopy
```

Tell the user the template is on the clipboard, ready to paste after `/compact`.
