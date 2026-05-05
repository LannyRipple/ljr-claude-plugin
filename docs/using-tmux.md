# using-tmux

Patterns for displaying output in separate tmux panes alongside Claude Code.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/using-tmux](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/using-tmux).

---

## The Core Idea

Claude Code runs in its own isolated tmux socket. This skill bridges that isolation
so Claude can open panes in your user tmux session and write output to them — live
status, logs, reference material, or an interactive shell — without cluttering the
main conversation.

---

## Display Modes

### Billboard (append-only)

Output is appended line by line to a persistent pane. Good for streaming status updates.

```
"show progress in a billboard pane"
"open a billboard and write status to it"
```

### Persistent billboard (file-backed)

Same as billboard but backed by a temp file. The pane can be re-opened and replayed
if it closes.

```
"use a persistent billboard for this"
```

### Show-and-go (one-shot)

Displays output once, then closes on Enter. Good for showing a result you don't need
to keep.

```
"show me that in a pane"
"show and go"
```

### Show-and-shell (output then interactive shell)

Shows output in a pane and then drops into an interactive shell for further exploration.

```
"show that output and leave a shell open"
"show and shell"
```

### Show-and-watch (live-updating)

Opens a pane running `watch` on a command for live updates.

```
"watch the build output in a pane"
```

---

## Things Worth Knowing

**Used by other skills.** `dev-panes`, `bye`, and others build on this skill's patterns.
If you're writing a skill that needs pane output, read this skill first.

**Not for agent team pane management.** Spawning Claude instances or sending keys to
run commands in agent teams is handled by Nelson/TeamCreate, not this skill.

**Requires tmux.** The skill checks for an active user tmux session and reports if one
isn't found.
