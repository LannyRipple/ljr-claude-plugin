#!/usr/bin/env bash
# Bump the patch version in both .claude-plugin JSON manifests.
# Usage: bump-version.sh [major|minor|patch]  (default: patch)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"

PART="${1:-patch}"
case "$PART" in
  major|minor|patch) ;;
  *) echo "Usage: $(basename "$0") [major|minor|patch]" >&2; exit 1 ;;
esac

# Guard against double-bumping: skip if the version in the working file differs from HEAD.
committed=$(git -C "$REPO_ROOT" show HEAD:.claude-plugin/plugin.json | jq -r '.version')
current=$(jq -r '.version' "$PLUGIN_JSON")
if [ "$committed" != "$current" ]; then
  echo "plugin.json version already bumped ($committed -> $current) — skipping." >&2
  exit 0
fi
IFS='.' read -r major minor patch <<< "$current"

case "$PART" in
  major) major=$((major + 1)); minor=0; patch=0 ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  patch) patch=$((patch + 1)) ;;
esac

next="${major}.${minor}.${patch}"

# Update plugin.json
jq --arg v "$next" '.version = $v' "$PLUGIN_JSON" > "$PLUGIN_JSON.tmp" && mv "$PLUGIN_JSON.tmp" "$PLUGIN_JSON"

echo "$current -> $next"
