---
name: bye
description: >-
  Cleans up all tmux panes created by the using-tmux skill (billboard,
  persistent billboard, show-and-shell, dev-panes shell) and exits Claude
  Code via tmux send-keys after cleanup. Trigger when the user types /bye
  or asks to clean up panes before exiting.
---

# Bye

Clean up all tmux panes created during this session, then exit Claude Code.

## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow it unless you have a
  specific reason not to; note when you deviate and why.

Every MUST and SHOULD in this skill is paired with a rationale. Read the rationale before
deciding to deviate from a SHOULD — it describes what breaks when you skip it.

## Steps

All tmux commands require `dangerouslyDisableSandbox: true`. If `$TMUX_PANE`
is empty the user is not in tmux — skip pane cleanup, output `Panes cleaned up.
Ready for /exit.` in chat, and stop.

1. **List panes** — Get all panes in the current window:
   ```bash
   tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}:#{pane_current_command}"
   ```

2. **Identify panes to kill** — The Claude Code pane is `$TMUX_PANE`. Every
   other pane in the window was created by a using-tmux workflow and should
   be killed.

3. **Kill non-Claude panes** — For each pane ID that is not `$TMUX_PANE`:
   ```bash
   tmux kill-pane -t <pane-id>
   ```
   MUST NOT kill `$TMUX_PANE` here — killing it mid-execution aborts the skill
   before step 4 can run. The pane is closed cleanly in step 4 instead.
   MUST NOT use `kill-session` or `kill-server` — these destroy the user's entire
   tmux session, not just this window's panes.

4. **Exit** — Announce in chat first, then send keystrokes to the Claude Code pane:
   > Panes cleaned up. Exiting.

   ```bash
   tmux send-keys -t "$TMUX_PANE" '/exit' Enter
   tmux send-keys -t "$TMUX_PANE" 'tmux kill-pane -t "$TMUX_PANE"' Enter
   ```

   The first send-keys exits Claude Code. The second sits in the input buffer —
   once Claude Code exits and the shell returns, the buffered command fires and
   closes the pane.
