# tmux Quick Reference

> **Note for Claude:** If the full man page needs to be regenerated to disk:
> ```bash
> mandoc -T markdown $(man -w tmux) > {path}.md
> ```
> `mandoc` is available via Homebrew and is the macOS equivalent of pandoc for man pages.
> The full man page is at `~/.claude/skills/using-tmux/references/tmux.1.md`.
>
> **Note:** The full man page path has moved to `~/.claude/skills/using-tmux/references/tmux.1.md`.

---

## Claude Code and tmux: Critical Architecture Notes

**Claude Code runs its own isolated tmux socket.** At startup, Claude creates a socket named
`claude-<PID>` and overrides the `TMUX` environment variable in all Bash tool subprocesses
to point to its own socket. This means:

- `tmux` commands run via Bash target **Claude's isolated session**, not the user's session
- The sandbox also blocks Unix socket access at `/private/tmp/tmux-<UID>/default`
- **To reach the user's tmux session**, you must use `dangerouslyDisableSandbox: true`

**Detecting whether you're inside tmux:** Claude captures the original `TMUX` env var at
module load (before overriding it). Check `$TMUX` is non-empty to know if the user started
Claude from inside tmux. Don't rely on running `tmux display-message` as a test — it will
succeed against Claude's own socket even if the user is not in tmux.

**`$TMUX_PANE`** is set by tmux to the current pane's ID (e.g., `%0`) and is captured at
startup. Use it to reliably reference the leader's pane even if the user switches panes.

**Agent teams** spawn full Claude instances via `send-keys -t paneId "command" Enter`.
Leader-to-teammate communication uses a file-based mailbox, not tmux directly. The socket
isolation (`-L <socket>`) lets swarm sessions run on a completely separate socket from the
user's session.

**Useful format variables** (used with `-F` flag or `display-message -p`):

| Variable | Meaning |
|----------|---------|
| `#{pane_id}` | Unique pane ID (e.g., `%3`) — stable for pane lifetime |
| `#{pane_current_command}` | Command running in pane |
| `#{pane_dead}` | `1` if pane's process has exited |
| `#{pane_title}` | Pane title (set with `select-pane -T`) |
| `#{session_name}` | Current session name |
| `#{window_index}` | Current window index |
| `#{socket_path}` | Path to tmux socket file |
| `#{pid}` | tmux server PID |

**Agent team layout pattern:**
```bash
# Leader at 30%, teammates fill the remaining 70%
tmux select-layout -t session:window main-vertical
tmux resize-pane -t <leader-pane-id> -x 30%
```

**Hide/show panes between sessions:**
```bash
# Hide: move pane to a detached session
tmux break-pane -d -s <pane-id> -t hidden-session:

# Show: bring it back
tmux join-pane -h -s <pane-id> -t target-window
```

---

## Target Addressing

Targets take the form `[session]:[window].[pane]`. Components can be omitted to use current context.

```
.1                  # pane 1 of current window in current session
mywindow.0          # pane 0 of window named "mywindow" in current session
mysession:1.0       # pane 0 of window 1 in session "mysession"
```

**Sessions** — matched in order: `$id`, exact name, name prefix, glob pattern. Prefix with `=` to force exact match.

**Windows** — `session:window`; window can be index, `@id`, exact name, name prefix, or glob. Special tokens:

| Token | Meaning |
|-------|---------|
| `{start}` / `^` | Lowest-numbered window |
| `{end}` / `$` | Highest-numbered window |
| `{last}` / `!` | Previously current window |
| `{next}` / `+` | Next window by number |
| `{previous}` / `-` | Previous window by number |

**Panes** — appended as `.pane` to a window target. Special tokens:

| Token | Meaning |
|-------|---------|
| `{last}` / `!` | Previously active pane |
| `{next}` / `+` | Next pane by number |
| `{previous}` / `-` | Previous pane by number |
| `{top}`, `{bottom}`, `{left}`, `{right}` | Edge panes |
| `{up-of}`, `{down-of}`, `{left-of}`, `{right-of}` | Relative to active pane |

**Unique IDs** — sessions prefixed `$`, windows `@`, panes `%`. Stable for the life of the object.
`$TMUX_PANE` environment variable contains the current pane's ID.

---

## Commands

### split-window (alias: splitw)
```
tmux split-window [-bdfhIvPZ] [-c start-dir] [-l size] [-t target-pane] [shell-command]
```
- `-v` — vertical split (panes stacked, default); `-h` — horizontal split (panes side by side)
- `-d` — do NOT make the new pane active (keeps focus on current pane) ← **use this to avoid stealing focus**
- `-b` — create pane to the left of or above target
- `-f` — span full window width (with `-v`) or height (with `-h`) instead of splitting active pane
- `-l size` — size in lines/columns; append `%` for percentage (e.g. `-l 30%`)
- `-Z` — zoom if not zoomed, keep zoomed if already zoomed
- `''` (empty shell-command) — creates pane with no running process; `display-message` can write to it
- `-I` — creates empty pane and forwards stdin to it (e.g. `make 2>&1 | tmux splitw -dI &`)

### kill-pane (alias: killp)
```
tmux kill-pane [-a] [-t target-pane]
```
- Destroys the pane. If it's the last pane, the window is also destroyed.
- `-a` — kill all panes *except* the one given with `-t`

### select-pane (alias: selectp)
```
tmux select-pane [-DdeLlMmRUZ] [-T title] [-t target-pane]
```
- Makes target-pane the active pane
- `-D`/`-L`/`-R`/`-U` — select pane below/left/right/above the target
- `-d` / `-e` — disable / enable input to the pane
- `-T title` — set pane title
- `-m` / `-M` — set / clear the marked pane (used as default source for join/swap)

### list-panes (alias: lsp)
```
tmux list-panes [-as] [-F format] [-f filter] [-t target]
```
- Default: lists panes in current window
- `-s` — target is a session, list all panes in it
- `-a` — list all panes on the server
- `-F` — custom format string (see FORMATS section of man page)

Useful format example:
```bash
tmux list-panes -F "#{pane_index}: cmd=#{pane_current_command} pid=#{pane_pid} dead=#{pane_dead}"
```

### list-windows (alias: lsw)
```
tmux list-windows [-a] [-F format] [-f filter] [-t target-session]
```
- Default: lists windows in current session
- `-a` — list all windows on the server

### send-keys (alias: send)
```
tmux send-keys [-FHKlMRX] [-N repeat-count] [-t target-pane] [key ...]
```
- Sends keystrokes to a pane. If string is not a key name, sent as literal characters.
- `-l` — treat all input as literal UTF-8 (disables key name lookup)
- `-R` — reset terminal state first
- Without `Enter` appended, text is typed but not submitted
- **Note:** For panes with no running process, send-keys has no effect.

### display-message (alias: display)
```
tmux display-message [-aCIlNpv] [-c target-client] [-d delay] [-t target-pane] [message]
```
- Without `-p`: displays message in the **status line** of the target client for `delay` ms (uses `display-time` option if delay omitted; `0` waits for keypress)
- `-p` — prints message to **stdout** instead (useful for scripting/capture)
- `-I` — forwards stdin to the empty pane given by `-t` ← **key for writing to `''` panes**
- `-l` — print message unchanged (skip format expansion)
- `-C` — keep pane updating while message is shown
- Message supports format variables (see FORMATS in full man page)

**Writing to an empty pane** (created with `split-window ''`):
```bash
echo "my text" | tmux display-message -I -t .1
```

### display-popup (alias: popup)
```
tmux display-popup [-BCEkN] [-h height] [-w width] [-x pos] [-y pos] [-T title] [-t target-pane] [shell-command]
```
- Shows a floating popup over panes running shell-command
- Panes are not updated while popup is visible
- `-E` — close popup when command exits
- `-B` — no border
- `-h`/`-w` — height/width in lines/columns or `%`
- `-x`/`-y` — position (default: centre)
- Useful for transient info display without a persistent pane

### pipe-pane (alias: pipep)
```
tmux pipe-pane [-IOo] [-t target-pane] [shell-command]
```
- Connects a pane's I/O to a shell command
- `-I` — pipe shell-command's stdout INTO the pane (write to pane)
- `-O` — pipe pane's output to shell-command's stdin (capture from pane, default)
- Both `-I` and `-O` can be used together
- `-o` — only open pipe if none exists (toggle-friendly)
- No shell-command: closes existing pipe

**Writing to a pane via pipe-pane:**
```bash
tmux pipe-pane -I -t .1 'cat ~/tmp/radar-display.txt'
```

### resize-pane (alias: resizep)
```
tmux resize-pane [-DLMRTUZ] [-t target-pane] [-x width] [-y height] [adjustment]
```
- `-U`/`-D`/`-L`/`-R` — resize up/down/left/right by adjustment (default 1)
- `-x`/`-y` — absolute size in lines/columns or `%`
- `-Z` — toggle zoom on active pane

### respawn-pane (alias: respawnp)
```
tmux respawn-pane [-k] [-c start-dir] [-t target-pane] [shell-command]
```
- Reactivates a dead pane (one whose command has exited)
- `-k` — kill any running command first
- Useful for restarting a `tail -f` display pane that died

---

## Workflow 1: Billboard Mode (pipe-pane -I)

Best for: append-only display without a backing file. Primary display workflow.
See `workflow-1-billboard.md` for dynamic pane lookup — do not hardcode indices.

```bash
# Setup — run once per session (billboard above, Claude Code below)
tmux split-window -b -dv 'stty -echo; cat'

# Find billboard dynamically
BILLBOARD=$(tmux list-panes -F "#{pane_index}:#{pane_current_command}" | grep ':cat$' | cut -d: -f1)

# Write content — always start with \n*
tmux pipe-pane -I -t .$BILLBOARD 'printf "\n* Line 1\nLine 2\n"'

# Teardown
tmux kill-pane -t .$BILLBOARD
```

**Gotchas:**
- `stty -echo` is required — without it, input echoes once from tty and once from cat
- `pipe-pane -I` takes a shell command whose stdout feeds the pane's stdin — not a push pipe
- Each `pipe-pane -I` call replaces the previous pipe; repeated calls work fine for appending
- `display-message -I` requires a truly empty pane — errors with "pane is not empty" if cat is running
- Empty `''` panes exit immediately on macOS; `stty -echo; cat` stays alive reliably

---

## Workflow 2: Persistent Billboard (tail -f)

Best for: display backed by a file — survives without Claude, any process can update it.
See `workflow-2-persistent-billboard.md` for dynamic pane lookup.

```bash
# Setup
touch ~/tmp/radar-display.txt
tmux split-window -b -dv 'tail -f ~/tmp/radar-display.txt'

# Write content
echo "Hello" >> ~/tmp/radar-display.txt

# Replace all content
printf "Fresh content\n" > ~/tmp/radar-display.txt

# Teardown
BILLBOARD=$(tmux list-panes -F "#{pane_index}:#{pane_current_command}" | grep ':tail$' | cut -d: -f1)
tmux kill-pane -t .$BILLBOARD
rm ~/tmp/radar-display.txt
```

**Gotchas:**
- If the pane dies (e.g. file deleted), use `respawn-pane` to restart it
- `split-window` without `-d` steals focus — always use `-d`

---

## Workflow: One-Shot Display Pane (show-and-go / show-and-shell / show-and-watch)

Best for: showing the user a file, command output, or summary they can read then dismiss.

```bash
# show-and-go — wait for Enter, then pane closes (omit -d so pane is active for input)
tmux split-window -v 'cat ~/some-file.txt; echo; read -p "[Press Enter to close]"'
tmux split-window -v 'some-command 2>&1; echo; read -p "[Press Enter to close]"'

# show-and-shell — output then interactive shell (omit -d so pane is active)
tmux split-window -v 'some-command 2>&1; exec bash'

# show-and-watch — live-updating monitor, Ctrl-C to kill (use -d, focus stays with user)
tmux split-window -dv 'watch -n 5 some-command'

# Large output — let user scroll
tmux split-window -v 'less ~/some-file.txt'
```

**Gotchas:**
- Pane closes as soon as command exits — use `read`, `exec bash`, `less`, or `watch` to keep open
- `exec bash` replaces the subshell cleanly; plain `bash` adds a subshell layer
- Omit `-d` for show-and-go and show-and-shell so the pane is active for user input
- Use `-d` for show-and-watch so focus stays with the user's current pane
- `remain-on-exit on` is another option — leaves a `[dead]` pane visible, requires manual close

---

## Semicolons in Shell Commands

When chaining tmux commands from the shell, semicolons must be escaped:

```bash
tmux neww \; splitw -d        # correct
tmux 'neww;' splitw -d        # also correct (quoted)
tmux neww; splitw -d          # WRONG — shell interprets ; as command separator
```
