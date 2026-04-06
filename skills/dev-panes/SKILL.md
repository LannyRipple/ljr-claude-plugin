---
name: dev-panes
description: >-
  Sets up the two-pane dev layout: left bash shell in the current working
  directory, Claude Code on the right. Trigger when the user types /dev-panes
  or asks for a two-pane, double-pane, or dev layout.
---

# Dev Panes

Run `~/.claude/plugins/marketplaces/ljr-marketplace/skills/dev-panes/scripts/setup-dev-panes.sh` with `dangerouslyDisableSandbox: true`,
passing the current working directory as the first argument.

Interpret the output:

- **`ALREADY_EXISTS:<id>`** — Tell the user a shell pane already exists (pane `<id>`);
  nothing was changed.
- **`CREATED:<id>`** — Tell the user the dev layout is ready (shell pane `<id>` on the
  left, Claude Code on the right).
- **Non-zero exit (check stderr for the `ERROR:` message)** — Show the error message to the user
  and ask whether to investigate the cause or fall back to the general `using-tmux` skill
  for manual setup.
