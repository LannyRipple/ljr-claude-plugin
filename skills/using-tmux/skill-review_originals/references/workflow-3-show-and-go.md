# Workflow 3: One-Shot Display Pane (show-and-go / show-and-shell / show-and-watch)

**Use for:** Showing the user something — command output, a file, a summary — in a pane
they can read and then dismiss or continue working in.

All variants use `-b` to open at the top (billboard position). After opening, the new
pane is `.0` and Claude Code shifts to `.1`.

**Verified working** in sessions with `dangerouslyDisableSandbox: true`.

## Show-and-go (press Enter to close)

```bash
# Show a file
tmux split-window -bv 'cat ~/some-file.txt; echo; read -p "[Press Enter to close]"'

# Show command output
tmux split-window -bv 'some-command 2>&1; echo; read -p "[Press Enter to close]"'
```

The `echo` before `read` adds a blank line so the prompt doesn't run up against the output.
Omit `-d` so the new pane is active and ready to receive the Enter keypress.

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
- For large output, consider `less` instead of `cat`: `tmux split-window -bv 'less ~/file.txt'`
