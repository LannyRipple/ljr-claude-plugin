# Workflow 1: Billboard Mode — Reference for Other Skills

## What It Is

A persistent display pane running `stty -echo; cat`, positioned above Claude Code.
Content is written via `pipe-pane -I`. Each write appends to the pane — nothing is
ever cleared automatically.

## Standard Layout

```
pane .0  — billboard (stty -echo; cat)    ← top
pane .1  — Claude Code                    ← bottom
```

This layout results from `tmux split-window -b -dv 'stty -echo; cat'` run from the
Claude Code pane. The `-b` flag places the new pane above, which tmux numbers .0,
pushing Claude Code to .1.

**Do not hardcode `.0`.** Use dynamic lookup (see below) — the index can shift if
other panes are present.

## Finding the Billboard Pane

`$TMUX_PANE` is the pane ID of the current shell, set automatically by tmux at startup
(e.g. `%2`). Use it to scope lookups to this Claude's window — multiple Claude instances
may run in separate windows.

Use pane IDs (`%N`) rather than indices; IDs are globally unique across windows.

```bash
BILLBOARD=$(tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}:#{pane_current_command}" | grep ':cat$' | cut -d: -f1)
```

If `$BILLBOARD` is empty, the billboard is not running. Set it up first:

```bash
if [ -z "$BILLBOARD" ]; then
  tmux split-window -b -dv -l 40% -t "$TMUX_PANE" 'stty -echo; cat'
  BILLBOARD=$(tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}:#{pane_current_command}" | grep ':cat$' | cut -d: -f1)
fi
```

## Writing to the Billboard

```bash
tmux pipe-pane -I -t "$BILLBOARD" 'printf "\n* Your content here\n"'
```

**Always start with `\n*`** — the newline separates outputs visually, and `*` mirrors
the Claude Code TUI dot effect.

For multi-line content:

```bash
tmux pipe-pane -I -t "$BILLBOARD" 'printf "\n* Title\nLine one\nLine two\n"'
```

## Checking Health

```bash
tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}: cmd=#{pane_current_command} dead=#{pane_dead}"
```

A healthy billboard pane shows `cmd=cat dead=0`. If `dead=1`, respawn it:

```bash
tmux respawn-pane -k -t "$BILLBOARD" 'stty -echo; cat'
```

## Teardown

```bash
tmux kill-pane -t "$BILLBOARD"
```

## Gotchas

- `stty -echo` is required — without it, text appears twice (tty echo + cat output)
- `pipe-pane -I` takes a shell command whose stdout feeds the pane's stdin — it is NOT a pipe you push to directly
- Each `pipe-pane -I` call replaces the previous pipe, so repeated calls are fine for appending
- `display-message -I` requires the pane to be truly empty (no running process) — errors with "pane is not empty". Use `pipe-pane -I` instead (this workflow's standard approach)
- Empty `''` panes exit immediately on macOS; `stty -echo; cat` stays alive reliably
- `sleep infinity` and `sleep INF` are Linux-isms — macOS BSD `sleep` only accepts numeric values
