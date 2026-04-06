#!/usr/bin/env bash
# bye.sh — Kill all non-Claude panes in the current tmux window, then exit.
#
# Usage: bye.sh
#
# Output (stdout):
#   NOT_IN_TMUX          — TMUX_PANE is unset; nothing to clean up
#   CLEANED:<n>          — killed <n> panes; caller should now send /exit + kill-pane
#
# Exit codes:
#   0 — success (either case above)
#   1 — a tmux command failed unexpectedly

set -euo pipefail

if [[ -z "${TMUX_PANE:-}" ]]; then
    echo "NOT_IN_TMUX"
    exit 0
fi

killed=0

while IFS=: read -r pane_id _cmd; do
    [[ "$pane_id" == "$TMUX_PANE" ]] && continue
    tmux kill-pane -t "$pane_id" || true
    killed=$(( killed + 1 ))
done < <(tmux list-panes -F "#{pane_id}:#{pane_current_command}")

echo "CLEANED:${killed}"
