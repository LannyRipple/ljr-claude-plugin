---
name: google-workspace-access
description: Access and edit Google Docs, Google Sheets, Google Slides, and Drive files using Google REST APIs, with browser automation fallback when API auth or write tools are unavailable. Use when the user mentions docs.google.com links, Google Docs, Google Sheets, spreadsheets, Google Slides, presentations, Drive files, or editing Google Workspace content.
---

# Google Workspace Access

## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow it unless you have a
  specific reason not to; note when you deviate and why.

Every MUST and SHOULD in this skill is paired with a rationale. Read the rationale before
deciding to deviate from a SHOULD — it describes what breaks when you skip it.

## Default Approach

Use direct Google REST APIs with a token from `gcloud`. This is the default workflow because it keeps working even when the `gws` CLI (a Google Workspace command-line tool, if the user has it installed) fails with `Not in a workspace`.

- Use `Drive API` for file lookup, metadata, and Google Doc export.
- Use `Docs API` for Google Docs structure and edits.
- Use `Sheets API` for spreadsheet reads, writes, and formatting.
- Use `Slides API` for Google Slides and presentations.

Use the `gws` CLI only if it is already working. Do not depend on it.

## Preconditions

1. Verify `gcloud` exists:

```bash
command -v gcloud
```

2. Check the active account:

```bash
gcloud config get-value account
```

3. Get a token:

```bash
TOKEN="$(gcloud auth print-access-token)"
```

4. If sandboxing blocks `~/.config/gcloud` or `credentials.db`, stop and ask the user to run the command directly in their terminal or with sandbox restrictions lifted.

5. If authentication fails with `401` or `403`, ask the user to run:

```bash
gcloud auth login --enable-gdrive-access --force --brief
```

6. If the error is `403 "Caller does not have required permission to use project"`, ask the user to run:

```bash
gcloud auth application-default revoke --quiet
```

If `gcloud` is not installed yet, follow the install and first-time setup steps in `${CLAUDE_SKILL_DIR}/references/api-reference.md`.

## File IDs

Extract file IDs from Google URLs:

- Docs: `https://docs.google.com/document/d/<FILE_ID>/edit`
- Sheets: `https://docs.google.com/spreadsheets/d/<FILE_ID>/edit`
- Slides: `https://docs.google.com/presentation/d/<FILE_ID>/edit`

`Google presentations` and `Google Slides` are the same product. Use the Slides API for both.

## Read Workflows

### Google Docs

- File metadata: `Drive API`
- Export readable content: `Drive API` export as `text/markdown`
- Inspect structure and indices for edits: `Docs API`

### Google Sheets

- Spreadsheet metadata: `Sheets API`
- Plain values: `values:batchGet`
- Formatting, links, and cell metadata: `includeGridData=true`

### Google Slides

- File metadata: `Drive API`
- Presentation structure and text content: `Slides API`

### Google Drive Search

Use the `Drive API` when the user needs to find files by name, MIME type, or text content.

## Edit Workflows

### Google Docs

Use `documents:batchUpdate`.

- Insert text first.
- Re-read the document.
- Apply paragraph and text styling in a second pass because indices shift after insertion.

### Google Sheets

Use:

- `values:batchUpdate` for cell values
- `spreadsheets:batchUpdate` for formatting, links, notes, and layout

If cells render like hyperlinks but are not real links, inspect formatting metadata and clear:

- `userEnteredFormat.textFormat.underline`
- `userEnteredFormat.textFormat.foregroundColor`
- `userEnteredFormat.textFormat.foregroundColorStyle`

### Google Slides

Use `presentations:batchUpdate`.

Common requests:

- `createSlide`
- `createShape`
- `insertText`
- `replaceAllText`
- `updateTextStyle`
- `updateShapeProperties`

Re-read the presentation after major edits if object IDs, indices, or layout assumptions may have changed.

## Browser Automation Fallback

Use browser automation when:

- `gcloud` is unavailable
- Google API auth is blocked
- Workspace write tools are blocked by OAuth admin policy
- The user explicitly wants UI-driven editing

For Google Sheets, use this sequence:

1. Navigate directly to the target cell with the URL `range` parameter.
2. Confirm the selected cell in the Name Box.
3. Activate edit mode from the formula bar, not from the grid.
4. Type into the hidden accessibility textbox for that cell.
5. Commit by moving focus away from the cell, usually by clicking the Name Box.
6. Repeat one cell at a time. Do not depend on Enter, Tab, or arrow-key navigation.

Detailed browser automation steps are in `${CLAUDE_SKILL_DIR}/references/api-reference.md`.

## Assistant Rules

1. MUST prefer `curl` or a short `python3` script over fragile shell parsing.
2. MUST report exact auth or permission errors and stop instead of guessing — partial success masks auth failures that surface later.
3. MUST NOT claim access worked until metadata or content reads succeed.
4. SHOULD use `Drive API` first for file metadata and discovery.
5. MUST NOT overwrite existing spreadsheet content unless the user explicitly asks to replace it.
6. MUST NOT add unintended link formatting when writing to Sheets.
7. SHOULD prefer API access and use browser automation only as a fallback.

## Additional Resources

Before making any API call, read `${CLAUDE_SKILL_DIR}/references/api-reference.md` for endpoint examples, field names, and request body patterns. Also consult it for troubleshooting auth errors and for the browser automation sequence.
