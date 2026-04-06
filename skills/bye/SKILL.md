---
name: bye
description: >-
  Cleans up all tmux panes created by the using-tmux skill (billboard,
  persistent billboard, show-and-shell, dev-panes shell) and exits Claude
  Code via tmux send-keys after cleanup. Trigger when the user types /bye
  or asks to clean up panes before exiting.
---

# Bye

Run `~/.claude/plugins/marketplaces/ljr-marketplace/skills/bye/scripts/bye.sh`
with `dangerouslyDisableSandbox: true`.

Interpret the output:

- **`NOT_IN_TMUX`** — Tell the user they are not in tmux; no panes to clean up.
  Do not send `/exit` or any tmux commands. Stop here.

- **`CLEANED:<n>`** — If `<n>` is 0, tell the user there were no extra panes to clean
  up. If `<n> > 0`, tell the user `<n>` pane(s) were removed. In both cases, using
  `dangerouslyDisableSandbox: true`, send the exit sequence to `$TMUX_PANE`:
  ```bash
  tmux send-keys -t "$TMUX_PANE" '/exit' Enter
  tmux send-keys -t "$TMUX_PANE" 'tmux kill-pane -t "$TMUX_PANE"' Enter
  ```
  The first keystroke exits Claude Code. The second sits in the shell buffer —
  once Claude Code exits and the shell returns, it fires and closes the pane.

- **Non-zero exit** — Show the stderr error to the user and stop. Do not attempt
  to send `/exit`.
