#!/usr/bin/env python3
"""
Auto-approve Bash and Read tool calls originating from the ljr-marketplace.

Installs as a PreToolUse hook. Returns {"allow": true} for any Bash command
or Read path under ~/.claude/plugins/marketplaces/ljr-marketplace/, suppressing
the permission prompt for skills the user explicitly invoked.
"""
import json
import os
import sys

MARKETPLACE_ROOT = os.path.expanduser("~/.claude/plugins/cache/ljr-marketplace/")

def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool == "Bash":
        command = os.path.expanduser(tool_input.get("command", ""))
        if MARKETPLACE_ROOT in command:
            print(json.dumps({"allow": True}))
    elif tool == "Read":
        file_path = tool_input.get("file_path", "")
        expanded = os.path.expanduser(file_path)
        if expanded.startswith(MARKETPLACE_ROOT):
            print(json.dumps({"allow": True}))

if __name__ == "__main__":
    main()
