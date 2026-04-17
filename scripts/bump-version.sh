#!/usr/bin/env bash
# Bump the patch version in both .claude-plugin JSON manifests.
# Usage: bump-version.sh [major|minor|patch]  (default: patch)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"
MARKET_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"

PART="${1:-patch}"
case "$PART" in
  major|minor|patch) ;;
  *) echo "Usage: $(basename "$0") [major|minor|patch]" >&2; exit 1 ;;
esac

# Read the current version from plugin.json (authoritative)
current=$(jq -r '.version' "$PLUGIN_JSON")
IFS='.' read -r major minor patch <<< "$current"

case "$PART" in
  major) major=$((major + 1)); minor=0; patch=0 ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  patch) patch=$((patch + 1)) ;;
esac

next="${major}.${minor}.${patch}"

# Update plugin.json
jq --arg v "$next" '.version = $v' "$PLUGIN_JSON" > "$PLUGIN_JSON.tmp" && mv "$PLUGIN_JSON.tmp" "$PLUGIN_JSON"

# Update marketplace.json: plugins[0].version and metadata.version
jq --arg v "$next" '
  .plugins[0].version = $v |
  .metadata.version   = $v
' "$MARKET_JSON" > "$MARKET_JSON.tmp" && mv "$MARKET_JSON.tmp" "$MARKET_JSON"

echo "$current -> $next"
