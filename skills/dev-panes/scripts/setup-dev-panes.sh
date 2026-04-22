#!/usr/bin/env bash
# setup-dev-panes.sh — Create or identify the left bash shell pane.
#
# Usage: setup-dev-panes.sh [working-dir]
#
# Output (stdout):
#   ALREADY_EXISTS:<pane-id>   — a bash pane other than the caller already exists
#   CREATED:<pane-id>          — new pane was created successfully
#
# Exit codes:
#   0 — success (either case above)
#   1 — not in tmux, or split-window failed

set -euo pipefail

WORKDIR="${1:-$PWD}"

if [[ -z "${TMUX_PANE:-}" ]]; then
    echo "ERROR: not running inside a tmux session (TMUX_PANE is unset)" >&2
    exit 1
fi

# Look for any pane in this window that is not the caller's pane.
existing=$(tmux list-panes -F "#{pane_id}" \
    | awk -v self="$TMUX_PANE" '$1 != self { print $1; exit }')

if [[ -n "$existing" ]]; then
    echo "ALREADY_EXISTS:${existing}"
    exit 0
fi

# Split: place new pane to the left (-b), horizontal split (-h), capture id.
new_pane=$(tmux split-window -bhP -F "#{pane_id}" -c "$WORKDIR" 'exec bash') || {
    echo "ERROR: tmux split-window failed" >&2
    exit 1
}

echo "CREATED:${new_pane}"
