# bye

Cleans up tmux panes created by `using-tmux` skills and exits Claude Code.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/bye](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/bye).

---

## What This Skill Does

When you're done with a session, `/bye` tears down any display panes opened during
the session (billboard, persistent billboard, show-and-shell, dev-panes shell) and
then kills the tmux session, which closes Claude Code with it.

If you're not in tmux, it reports that and stops — it won't attempt any cleanup or exit.

---

## Usage

```
/bye
"clean up and exit"
```

No arguments needed.

---

## Things Worth Knowing

**Only removes panes created by this plugin.** It won't close panes you opened yourself
or panes from other tools. The script tracks which panes it owns by naming convention.

**Kills the tmux session, not just the pane.** The exit is done via `tmux kill-session`,
which terminates everything in the session including Claude Code. There's no "soft" exit.

**If you have unsaved work in a shell pane**, save it before running `/bye`. The pane
will be gone along with any unsaved state in it.
