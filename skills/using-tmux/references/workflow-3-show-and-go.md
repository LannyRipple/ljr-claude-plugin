# Workflow 3: One-Shot Display Pane (show-and-go / show-and-shell / show-and-watch)

**Use for:** Showing the user something — command output, a file, a summary — in a pane
they can read and then dismiss or continue working in.

All variants use `-b` to open at the top (billboard position). After opening, the new
pane is `.0` and Claude Code shifts to `.1`.

**Sandbox bypass is required.** All variants need `dangerouslyDisableSandbox: true` to reach
the user's tmux session. If you cannot set it, tell the user and stop — the workflow will
not work without it.

## Show-and-go (q to close)

Prefer `less` — it is scrollable, searchable with `/`, and `q` to dismiss is intuitive.

```bash
# Show a file (preferred)
tmux split-window -bv 'less ~/some-file.txt'

# Show command output (preferred)
tmux split-window -bv 'some-command 2>&1 | less'
```

Use `cat + read` only for short, known-length output where `less` would feel like overkill
(e.g., a 3-line status message):

```bash
# Short output fallback
tmux split-window -bv 'some-command 2>&1; echo; read -p "[Press Enter to close]"'
```

The `echo` before `read` adds a blank line so the prompt doesn't run up against the output.
Omit `-d` so the new pane is active and ready to receive input.

## Show-and-shell (output then interactive shell)

```bash
tmux split-window -bv 'some-command 2>&1; exec bash'
```

`exec bash` replaces the subshell cleanly — no extra shell layer, pane stays alive until
the user exits.

## Show-and-watch (live-updating, Ctrl-C to kill)

```bash
tmux split-window -bdv 'watch -n 5 some-command'
```

Good for monitoring — `watch` reruns the command on an interval. `-d` keeps focus on the
current pane since the user will Ctrl-C from there when done.

## Gotchas

- The pane is NOT managed by Claude after creation — the user interacts with it directly
- Omit `-d` for show-and-go and show-and-shell so the pane is immediately active
- Use `-d` for show-and-watch so focus stays with the user's current pane
- Prefer `less` over `cat + read` — see the show-and-go section above for the canonical patterns
