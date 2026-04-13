# Memory File Structure

## Location and format

The memory file is `~/Library/CloudStorage/GoogleDrive-lripple@salesforce.com/My Drive/radar-memory.md`. It has two parts:
1. **YAML frontmatter** at the top — metadata Radar reads and updates
2. **Markdown sections** — one per category of entry

## Frontmatter

```yaml
---
last-date-check: YYYY-MM-DD
created: YYYY-MM-DD
version: N
---
```

- `version`: monotonically increasing integer; incremented on every write for optimistic locking

Add new frontmatter fields as needed. If tracking some persistent context becomes useful
(e.g., a recurring meeting cadence, a project milestone), a new field can go here. The
frontmatter is Radar's scratchpad for metadata that needs to survive across sessions.

## Sections

Standard sections to create on first use:

| Section | Purpose |
|---|---|
| `## TODO` | Action items the user owns |
| `## Appointments` | Scheduled events with a date and time |
| `## Reminders` | Things to remember; may or may not be time-bounded |
| `## Notes` | Reference info — people, context, decisions, background |

Add new sections when a clear pattern emerges. `## Projects`, `## People`, and
`## Waiting On` are natural extensions. The goal is a file that's easy to scan,
not a rigid schema the user has to think about.

## Entry format

Every entry gets a `YYYY-MM-DD` date stamp so staleness can be assessed later.
When you surface an entry as a reminder, update its date stamp to today so the interval resets and the entry stays fresh.

**TODO**
```
- [ ] 2026-03-26 Review the infra cost report
- [x] 2026-03-20 Send Q1 summary to Pradeep
```
Use `[ ]` for open items and `[x]` for completed ones. Completed items accumulate over time
and can be cleaned up during a date check.

**Appointments**
```
- 2026-03-27 Thursday 10am MLS team sync
- 2026-04-01 Wednesday 2pm 1:1 with Pradeep
```

**Reminders**
```
- 2026-03-25 Talk to Jordan Sarkodie about the deployment schedule
- 2026-03-20 Ask Richard about the new API auth approach
```

**Notes**
```
- 2026-03-26 Pradeep mentioned the V2MOM review is moving to April
- 2026-03-15 Prediction service latency spike was traced to the scone upgrade
```

## Writing entries

Use natural language — these are notes, not database records. The date stamp is the only
required structure.

After writing, confirm briefly:
> *"Got it — I've added that to your TODO: review the infra cost report (2026-03-26)."*

If it's not clear what's meant — which section, or what exactly to note — ask one clarifying
question before writing. Getting it right matters more than speed — a misrecorded note
creates confusion later.

## Writing (with optimistic locking)

The memory file lives in Google Drive and could in principle be open in another
session on another machine. Use optimistic locking on every write:

1. Read the file; record the current `version: N`.
2. Apply the desired change in memory.
3. Re-read the file and confirm `version` is still `N`.
4. If still `N`: write the full updated file with `version: N+1` using the Write tool.
5. If version has changed: report a conflict — show the current file state and ask
   the user whether to retry or abandon.
