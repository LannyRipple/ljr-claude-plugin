---
name: dev-panes
description: >-
  Sets up the two-pane dev layout: left bash shell in the current working
  directory, Claude Code on the right. Trigger when the user types /dev-panes
  or asks for a two-pane, double-pane, or dev layout.
---

# Dev Panes

Invoke the `using-tmux` skill. Using that skill's pane-state reference, check
whether a left shell pane already exists. If one is found, notify the user and
stop without splitting. Otherwise, open a left bash shell pane in the current
working directory (show-and-shell workflow), leaving Claude Code on the right.
