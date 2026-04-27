# Google Workspace Reference

## Installation and Setup

This skill's default path depends on a local `gcloud` install because it uses:

```bash
gcloud auth print-access-token
```

to get a Google access token for the Drive, Docs, Sheets, and Slides APIs.

If `gcloud` is unavailable, use the browser automation fallback instead of forcing the API path.

### macOS via Homebrew

This matches the working setup used in local Cursor sessions.

Install:

```bash
brew install --cask gcloud-cli
```

Verify:

```bash
command -v gcloud
gcloud version
```

If Homebrew shows the `gcloud-cli` caveat about PATH, add:

```bash
export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
```

to your shell profile, then open a new shell and re-run:

```bash
command -v gcloud
```

### First-Time Authentication

Authenticate with Google Workspace access enabled:

```bash
gcloud auth login --enable-gdrive-access --force --brief
```

Then verify the active account:

```bash
gcloud config get-value account
```

Then verify token retrieval:

```bash
gcloud auth print-access-token
```

Expected result:

- a long bearer token string means the API path is ready
- auth errors mean the user needs to refresh login or fix local `gcloud` setup

### What This Skill Uses `gcloud` For

- obtaining OAuth access tokens for Google APIs
- identifying the active Google account
- re-authenticating when tokens or account state are invalid

`gcloud` is not used for document editing itself. Editing is done through Google REST APIs or browser automation.

## Authentication

Check the local install and active account:

```bash
command -v gcloud
gcloud config get-value account
```

Get a token:

```bash
TOKEN="$(gcloud auth print-access-token)"
```

If auth fails:

```bash
gcloud auth login --enable-gdrive-access --force --brief
```

If the error is `Caller does not have required permission to use project`:

```bash
gcloud auth application-default revoke --quiet
```

## Useful MIME Types

| File type | MIME type |
|------|------|
| Google Doc | `application/vnd.google-apps.document` |
| Google Sheet | `application/vnd.google-apps.spreadsheet` |
| Google Slides | `application/vnd.google-apps.presentation` |
| Markdown export | `text/markdown` |
| PDF export | `application/pdf` |
| PPTX export | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |

## Extracting File IDs

Extract the ID between `/d/` and `/edit`:

- Docs: `https://docs.google.com/document/d/<FILE_ID>/edit`
- Sheets: `https://docs.google.com/spreadsheets/d/<FILE_ID>/edit`
- Slides: `https://docs.google.com/presentation/d/<FILE_ID>/edit`

## Drive API

Use Drive API for metadata, search, and exports.

### File Metadata

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files/${FILE_ID}?fields=id,name,mimeType,webViewLink"
```

### Search by Name or Text

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files?q=name%20contains%20'planning'%20and%20mimeType%20=%20'application/vnd.google-apps.spreadsheet'&fields=files(id,name,mimeType,webViewLink)"
```

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files?q=fullText%20contains%20'TrendDB'%20and%20mimeType%20=%20'application/vnd.google-apps.document'&fields=files(id,name,webViewLink)"
```

## Google Docs

Use:

- `Drive API` for metadata and markdown export
- `Docs API` for structure and edits

### Export a Doc as Markdown

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files/${DOC_ID}/export?mimeType=text/markdown"
```

### Read Document Structure

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://docs.googleapis.com/v1/documents/${DOC_ID}"
```

Use the `body.content` array to find paragraph text and insertion indices.

### Append Text to a Doc

Insert text first:

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "https://docs.googleapis.com/v1/documents/${DOC_ID}:batchUpdate" \
  -d @- <<'EOF'
{
  "requests": [
    {
      "insertText": {
        "location": { "index": 1 },
        "text": "New content here.\n"
      }
    }
  ]
}
EOF
```

Then re-read the document and apply styles in a second call because indices shift after insertion.

### Apply Paragraph or Text Style

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "https://docs.googleapis.com/v1/documents/${DOC_ID}:batchUpdate" \
  -d @- <<'EOF'
{
  "requests": [
    {
      "updateParagraphStyle": {
        "range": { "startIndex": 1, "endIndex": 20 },
        "paragraphStyle": { "namedStyleType": "HEADING_2" },
        "fields": "namedStyleType"
      }
    },
    {
      "updateTextStyle": {
        "range": { "startIndex": 21, "endIndex": 40 },
        "textStyle": { "bold": true },
        "fields": "bold"
      }
    }
  ]
}
EOF
```

## Google Sheets

Use:

- `values:batchGet` for plain values
- `includeGridData=true` when you need formatting, hyperlinks, or formulas
- `values:batchUpdate` for values
- `spreadsheets:batchUpdate` for formatting and layout

### Spreadsheet Metadata

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}?fields=properties.title,sheets.properties(title,sheetId,index,gridProperties)"
```

### Read Plain Values

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values:batchGet?ranges=Sheet1!A1:C10&ranges=Sheet1!F1:H20"
```

### Read Cell Formatting or Links

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}?ranges=Sheet1!F1:H20&includeGridData=true&fields=sheets(data(rowData(values(formattedValue,hyperlink,textFormatRuns,userEnteredValue,userEnteredFormat,effectiveFormat))))"
```

### Write Cell Values

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values:batchUpdate" \
  -d @- <<'EOF'
{
  "valueInputOption": "USER_ENTERED",
  "data": [
    {
      "range": "Sheet1!F4:G4",
      "majorDimension": "ROWS",
      "values": [
        [
          "Outcome text",
          "Objective and key details text"
        ]
      ]
    }
  ]
}
EOF
```

### Clear Hyperlink-Style Formatting

Sometimes a cell is not a true link, but it still renders blue and underlined because the format was inherited earlier. Clear that with `repeatCell`:

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}:batchUpdate" \
  -d @- <<'EOF'
{
  "requests": [
    {
      "repeatCell": {
        "range": {
          "sheetId": 0,
          "startRowIndex": 3,
          "endRowIndex": 54,
          "startColumnIndex": 5,
          "endColumnIndex": 7
        },
        "cell": {
          "userEnteredFormat": {
            "textFormat": {
              "foregroundColor": {},
              "foregroundColorStyle": { "rgbColor": {} },
              "underline": false
            }
          }
        },
        "fields": "userEnteredFormat.textFormat.foregroundColor,userEnteredFormat.textFormat.foregroundColorStyle,userEnteredFormat.textFormat.underline"
      }
    }
  ]
}
EOF
```

## Google Slides

Use:

- `Drive API` for metadata or exports
- `Slides API` for structure and edits

### Read Presentation Structure

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://slides.googleapis.com/v1/presentations/${PRESENTATION_ID}"
```

### Export Slides to PDF

```bash
curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://www.googleapis.com/drive/v3/files/${PRESENTATION_ID}/export?mimeType=application/pdf" \
  --output deck.pdf
```

### Replace Text Everywhere

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "https://slides.googleapis.com/v1/presentations/${PRESENTATION_ID}:batchUpdate" \
  -d @- <<'EOF'
{
  "requests": [
    {
      "replaceAllText": {
        "containsText": {
          "text": "{{BUILD_NUMBER}}",
          "matchCase": true
        },
        "replaceText": "264"
      }
    }
  ]
}
EOF
```

### Create a Slide and Add Text

```bash
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "https://slides.googleapis.com/v1/presentations/${PRESENTATION_ID}:batchUpdate" \
  -d @- <<'EOF'
{
  "requests": [
    {
      "createSlide": {
        "objectId": "new_slide_1",
        "slideLayoutReference": {
          "predefinedLayout": "TITLE_AND_BODY"
        }
      }
    },
    {
      "createShape": {
        "objectId": "title_box_1",
        "shapeType": "TEXT_BOX",
        "elementProperties": {
          "pageObjectId": "new_slide_1",
          "size": {
            "height": { "magnitude": 60, "unit": "PT" },
            "width": { "magnitude": 400, "unit": "PT" }
          },
          "transform": {
            "scaleX": 1,
            "scaleY": 1,
            "translateX": 40,
            "translateY": 40,
            "unit": "PT"
          }
        }
      }
    },
    {
      "insertText": {
        "objectId": "title_box_1",
        "insertionIndex": 0,
        "text": "New slide content"
      }
    }
  ]
}
EOF
```

For more complex edits, inspect the existing `pageElements` first and use real object IDs from the presentation.

## Browser Automation Fallback for Google Sheets

The browser automation workflow below covers Google Sheets only. For Google Docs and Slides, browser automation is not documented — if API access is unavailable for those products, surface the limitation to the user rather than attempting unsupported UI manipulation.

Use this only when API access or write tooling is unavailable. This is a fallback workflow for editing Sheets through the web UI one cell at a time.

### Strategy

1. Navigate to the spreadsheet with the target cell in the URL.
2. Activate edit mode through the formula bar.
3. Type into the hidden accessibility textbox for the selected cell.
4. Commit the edit by moving focus away from the cell.

Do not click random grid cells, and do not rely on Enter or Tab to commit.

### Navigate to the Target Cell

Use the `range` URL parameter to pre-select the cell:

```text
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={SHEET_GID}&range={CELL}
```

Example:

```text
https://docs.google.com/spreadsheets/d/1abc.../edit#gid=0&range=F15
```

### Verify Cell Selection

Use the browser accessibility snapshot or tree and confirm that the Name Box shows the expected cell reference, such as `F15`.

Key element:

- `Name box (⌘ + J)`

### Activate Edit Mode

Click the formula bar area, specifically the line-break element next to the Name Box, instead of clicking the grid cell directly. This keeps the current cell selected while entering edit mode.

### Confirm Edit Mode

After activating edit mode, re-read the accessibility tree and look for a textbox named after the selected cell, such as `F15`. This is the hidden accessibility textbox that accepts the cell value.

### Type the Cell Value

Type directly into the hidden textbox.

For formulas, include the leading `=`:

```text
=HYPERLINK("https://example.com", "Display Text")
```

### Commit the Edit

Commit the edit by moving focus away from the cell, usually by clicking the Name Box.

Do not depend on Enter or Tab. Browser typing helpers often insert text without dispatching the real key events that Google Sheets expects for commit.

### Verify the Edit

Verify with one of these:

- Re-read the spreadsheet through the Sheets API.
- Re-read the visible cell value in the browser UI.
- Look for early save signals such as `Saved to Drive`.

### Editing Multiple Cells

For each cell:

1. Navigate with a fresh `range` URL.
2. Enter edit mode.
3. Type into the hidden textbox.
4. Commit the edit.

Do not try to move between cells with arrow keys, Tab, or Enter.

### Common Mistakes

| Mistake | Fix |
|------|------|
| Clicking the grid to select cells | Always use the URL `range` parameter for precise cell targeting |
| Typing into the formula bar container directly | Activate edit mode first, then type into the hidden textbox for the selected cell |
| Pressing Enter or Tab to commit | Move focus away, usually by clicking the Name Box |
| Navigating while still editing | Commit first, then navigate to the next cell |
| Trying to batch-edit many cells from one page state | Re-navigate for each cell |

## Python Helper Pattern

Use Python when the request body is large or JSON parsing is awkward:

```python
import json
import subprocess
import urllib.request

token = subprocess.check_output(
    ["gcloud", "auth", "print-access-token"],
    text=True,
).strip()

url = "https://sheets.googleapis.com/v4/spreadsheets/<SHEET_ID>/values:batchGet?ranges=Sheet1!A1:C10"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

with urllib.request.urlopen(req) as resp:
    data = json.load(resp)

print(json.dumps(data, indent=2))
```

## Troubleshooting

### `gws` fails with `Not in a workspace`

Use direct Google APIs with `gcloud` instead of the `gws` CLI.

### Sandbox blocks `~/.config/gcloud`

Request elevated or unsandboxed permissions before retrying.

### `401` or `403`

Do not guess. Report the exact error, then ask the user to refresh `gcloud` auth.

### File access denied

The file may not be shared with the active Google account returned by:

```bash
gcloud config get-value account
```

### Sheets cells look like links after writing

Inspect `userEnteredFormat.textFormat` and clear underline and explicit link color with `repeatCell`.
