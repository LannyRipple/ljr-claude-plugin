---
name: dev-panes
description: >-
  Sets up the two-pane dev layout: left bash shell in the current working
  directory, Claude Code on the right. Trigger when the user types /dev-panes
  or asks for a two-pane, double-pane, or dev layout.
---

# Dev Panes

Invoke the `using-tmux` skill to open a left bash shell pane in the current
working directory (show-and-shell workflow), leaving Claude Code on the right.
Check first that a left shell pane doesn't already exist before splitting.
