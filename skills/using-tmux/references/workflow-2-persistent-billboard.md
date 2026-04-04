# Workflow 2: Persistent Billboard — Reference for Other Skills

## What It Is

A display pane running `tail -f` against a file on disk. Any process can update the
display by writing to the file — Claude does not need to be present. Use this when the
display needs to survive across sessions or be updated by non-Claude processes.

For Claude-only display within a session, prefer Workflow 1 (Billboard Mode).

## Standard Layout

```
pane .0  — persistent billboard (tail -f ~/tmp/radar-display.txt)  ← top
pane .1  — Claude Code                                              ← bottom
```

**Do not hardcode `.0`.** Use dynamic lookup (see below).

## Standard File Path

```
~/tmp/radar-display.txt
```

This path is the convention. Skills may use their own file if they have a distinct
persistent display, but should document it clearly.

## Finding the Persistent Billboard Pane

`$TMUX_PANE` is the pane ID of the current shell, set automatically by tmux at startup.
Use it to scope lookups to this window — multiple Claude instances may run in separate windows.
Use pane IDs (`%N`) rather than indices; IDs are stable for the pane's lifetime.

```bash
BILLBOARD=$(tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}:#{pane_current_command}" | grep ':tail$' | cut -d: -f1)
```

If `$BILLBOARD` is empty, the billboard is not running. Set it up:

```bash
if [ -z "$BILLBOARD" ]; then
  touch ~/tmp/radar-display.txt
  tmux split-window -b -dv -t "$TMUX_PANE" 'tail -f ~/tmp/radar-display.txt'
  BILLBOARD=$(tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}:#{pane_current_command}" | grep ':tail$' | cut -d: -f1)
fi
```

## Writing to the Persistent Billboard

```bash
# Append content
printf "\n* Your content here\n" >> ~/tmp/radar-display.txt

# Replace all content
printf "Fresh content\n" > ~/tmp/radar-display.txt
```

Write directly to the file — the `tail -f` pane updates automatically.

## Checking Health

```bash
tmux list-panes -t "$TMUX_PANE" -F "#{pane_id}: cmd=#{pane_current_command} dead=#{pane_dead}"
```

A healthy pane shows `cmd=tail dead=0`. If `dead=1`, respawn it:

```bash
tmux respawn-pane -k -t "$BILLBOARD" 'tail -f ~/tmp/radar-display.txt'
```

## Teardown

```bash
tmux kill-pane -t "$BILLBOARD"
rm ~/tmp/radar-display.txt
```

## Gotchas

- If the pane dies (e.g. file deleted out from under it), respawn it — see Checking Health above
