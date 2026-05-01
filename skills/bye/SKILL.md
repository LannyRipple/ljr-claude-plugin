---
name: bye
description: >-
  Cleans up all tmux panes created by the using-tmux skill (billboard,
  persistent billboard, show-and-shell, dev-panes shell) and exits Claude
  Code via tmux send-keys after cleanup. Trigger when the user types /bye
  or asks to clean up panes before exiting.
---

# Bye

Run `${CLAUDE_SKILL_DIR}/scripts/bye.sh`
with `dangerouslyDisableSandbox: true`.

Interpret the output:

- **`NOT_IN_TMUX`** — Tell the user they are not in tmux; no panes to clean up.
  Do not send `/exit` or any tmux commands. Stop here.

- **`CLEANED:<n>`** — If `<n>` is 0, tell the user there were no extra panes to clean
  up. If `<n> > 0`, tell the user `<n>` pane(s) were removed. In both cases, using
  `dangerouslyDisableSandbox: true`, kill the session:
  ```bash
  tmux kill-session
  ```
  This terminates the entire tmux session (including Claude Code) without requiring
  any keystrokes sent to the terminal.

- **Non-zero exit** — Show the stderr error to the user and stop. Do not attempt
  to send `/exit`.
