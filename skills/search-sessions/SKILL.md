---
name: search-sessions
description: "Search old session transcripts by keyword and show matching sessions with resume commands"
argument-hint: "search keywords"
disable-model-invocation: true
---

Search through all session transcript .jsonl files in `~/.claude/projects/` for the keyword(s): **$ARGUMENTS**

Follow these steps:

1. Run `grep` via the Bash tool to quickly identify which `.jsonl` files contain the search term anywhere in the file. By default, search only the `.jsonl` files under the project directory corresponding to the current working directory. If the user asks to search across all projects or says something like "search everywhere", search recursively across all directories under `~/.claude/projects/`. Use case-insensitive matching.

2. For each matching file, use python3 to parse the `.jsonl` content and extract matches only from user and assistant message content:
   - The session ID (the filename without .jsonl extension)
   - The project directory name (parent folder)
   - The timestamp of the first user message
   - The timestamp of the last message
   - The first real user message (not a `/clear` command, not a `<local-command-caveat>`, not a tool_result) - show the first 200 characters
   - Up to 3 snippets (under 100 chars each) showing where the search term appears in context

3. Present results as a numbered list, sorted by most recent first. For each result show:
   - Session date range
   - First user message preview
   - Matching snippets
   - The resume command: `claude --resume SESSION_ID`

4. If there are more than 10 matches, show only the 10 most recent and mention how many total were found.

5. If no matches are found, say so and suggest trying different keywords.

Use python3 for parsing the .jsonl files since they contain JSON. Use `dangerouslyDisableSandbox: true` on all Bash calls in this skill — the `.jsonl` files are outside the working directory and require sandbox bypass. Do NOT use Claude Code's built-in Grep tool — it cannot access paths outside the working directory.
