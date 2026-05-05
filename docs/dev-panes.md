# dev-panes

Sets up a two-pane tmux layout: shell on the left, Claude Code on the right.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/dev-panes](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/dev-panes).

---

## What This Skill Does

Opens a bash shell pane in the current working directory alongside the Claude Code
session. Useful when you want a terminal close at hand without switching windows.

```
/dev-panes
"set up dev panes"
"two-pane layout"
"open a shell pane"
```

If a shell pane already exists from a previous invocation, it reports that and does
nothing. Run `/bye` to tear it down when you're done.

---

## Things Worth Knowing

**The shell pane is yours.** Claude will ask before sending any commands to it — it
won't silently run things in your shell without confirmation.

**Pairs with `/bye`.** The pane is tracked by the plugin and will be closed when you
run `/bye` at the end of the session.

**Requires tmux.** If you're not in a tmux session, the skill reports that and stops.
