---
name: using-tmux
description: |
  Utilities and workflows for writing output to tmux display panes. Use when the user
  asks to display output in a separate pane, open a side panel, or use any of the named
  workflows: billboard (append-only display), persistent billboard (file-backed display),
  show-and-go (show output then close on Enter), show-and-shell (output then interactive
  shell), or show-and-watch (live-updating watch pane). Trigger on phrases like "show
  and go", "show me X in a pane", "open a side panel", "put that in a tmux pane",
  "billboard mode", "show-and-go", or any request to display content outside the main
  conversation pane.
  NOT for agent team pane management (spawning Claude instances, send-keys to run
  commands) — that is handled internally by the agent team tools (Nelson, TeamCreate).
---

# using-tmux

This skill provides Claude with the knowledge and workflows to interact with the user's
tmux session from within Claude Code Bash tool calls.

## Reference Material

The primary reference is `references/tmux-quick-reference.md`. Read it before using any
tmux commands. The full man page is at `references/tmux.1.md` if deeper detail is needed.

## Critical: Claude Code tmux Isolation

**Claude Code runs its own isolated tmux socket** (`claude-<PID>`). The `TMUX` environment
variable is overridden in all Bash tool subprocesses to point to Claude's socket. This means:

- Plain `tmux` commands in Bash will target Claude's session, NOT the user's
- The sandbox also blocks the Unix socket at `/private/tmp/tmux-<UID>/default`
- **Every tmux command that targets the user's session MUST use `dangerouslyDisableSandbox: true`**

This is not a workaround — it is the required approach. Without `dangerouslyDisableSandbox: true`,
tmux commands either fail silently or operate on Claude's invisible internal session.

## Workflow Routing

Determine the workflow from the request, then read the corresponding reference file.

| Workflow | Use for | Reference |
|----------|---------|-----------|
| 1 — Billboard | Append-only display, no backing file. Default choice. | `references/workflow-1-billboard.md` |
| 2 — Persistent Billboard | File-backed display, survives session end, any process can write | `references/workflow-2-persistent-billboard.md` |
| 3 — Show-and-* | One-shot display: show-and-go, show-and-shell, show-and-watch | `references/workflow-3-show-and-go.md` |

All workflows open the display pane at the top (`-b` flag). After opening, the display
pane is `.0` and Claude Code shifts to `.1`.

## Pane Index Stability

**Pane indices are not stable.** When a pane is killed, remaining panes are renumbered
from 0. Use dynamic lookup by running command (see workflow reference files) — any
hardcoded index will silently target the wrong pane after a kill.

**Numbering direction:** Panes are numbered left-to-right for horizontal splits (`-h`),
top-to-bottom for vertical splits (`-v`).

**Equal sizing:** Each `split-window` halves the space of the pane it splits. When
creating multiple panes, equalize after all splits are done:

```bash
tmux select-layout even-horizontal  # for side-by-side panes
tmux select-layout even-vertical    # for stacked panes
```

## Pane Addressing

```
.1                  # pane 1 of current window (most common for a display pane)
session:window.pane # fully qualified
```

Use `%`-prefixed IDs (e.g. `%3`) for stable references that survive window navigation.
`$TMUX_PANE` is set by tmux to the current pane's ID at startup.

## Checking Pane State

```bash
# List panes in current window with useful info
tmux list-panes -F "#{pane_index}: cmd=#{pane_current_command} pid=#{pane_pid} dead=#{pane_dead}"

# Check if pane .1 exists and is alive
tmux list-panes -F "#{pane_index}:#{pane_dead}" | grep "^1:0"
```

## Safety

- Always use `-d` on `split-window` to avoid stealing focus from the user (exception: show-and-go and show-and-shell omit `-d` intentionally)
- Never run `tmux kill-session` or `tmux kill-server` — this would destroy the user's session
- When in doubt about which pane is which, list panes before acting
- This skill is for **display/output panes only** — do not use it to spawn agent instances or send commands to agent panes. Agent team pane management is handled by the TeamCreate/Nelson tools internally.
- If the user uses agent teams (Nelson, etc.), panes may already be in use — check before creating

## Known Issues

**`/exit` with an active billboard leaves user in the billboard pane.** When Claude Code is exited via `/exit` while a billboard or persistent billboard pane is open, the tmux focus remains on the billboard pane rather than returning to the Claude Code pane. This is not fixable — `/exit` is a Claude Code built-in that fires outside of Claude's observation (no hook runs). The user must manually switch panes (`Ctrl-b o` or `Ctrl-b q <index>`) after `/exit`. Consider warning the user before setting up a long-running billboard session.
