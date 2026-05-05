# google-workspace-access

Read and edit Google Docs, Sheets, Slides, and Drive files.

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/google-workspace-access](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/google-workspace-access).

---

## What This Skill Does

Gives Claude access to your Google Workspace content — reading documents, editing
text, updating spreadsheet cells, browsing Drive. It uses the Google Workspace MCP
tools when available, with browser automation as a fallback.

Triggers automatically when you paste a `docs.google.com` link or ask about a Google
Doc, Sheet, Slide, or Drive file.

---

## Operations

### Read a document

```
"summarize this doc: docs.google.com/..."
"what's in the spreadsheet at [url]?"
"read my notes from the meeting doc"
```

### Edit a document

```
"add a section on error handling to this doc: [url]"
"update cell B3 in my tracking sheet to 'done'"
"append these findings to [doc url]"
```

### Browse Drive

```
"find my Q1 planning doc in Drive"
"list files in my MLS folder"
```

---

## Things Worth Knowing

**MCP tools are preferred.** The Google Workspace MCP server handles most operations
without needing a browser. If MCP tools aren't available or auth is expired, the skill
falls back to browser automation — which is slower but works for most read operations.

**Edits are direct.** There's no preview step — edits go straight to the document. If
you want to review before committing, say so and Claude will show the proposed change first.

**Spreadsheet edits are cell-level.** For bulk updates, specify the range explicitly
(e.g., "update A2:A10 with these values") rather than asking for a vague "update the
sheet" — cell-level is more reliable than document-level rewrites.
