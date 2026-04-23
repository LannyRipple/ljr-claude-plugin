# Gmail Check Procedure

Run this during agenda building. Use `mcp__plugin_gmail_gmail__gmail_search` for both
searches. Fetch subject, sender, and date only — do not retrieve full bodies.

## Filtering Pipeline

Apply all three filter stages in order. Discard a message if it matches any stage.

### Stage 1 — Sender address patterns

Discard if the sender address contains any of:
`noreply`, `no-reply`, `donotreply`, `do-not-reply`, `notification`, `automated`,
`workday`, `servicenow`, `mailer-daemon`, `postmaster`, `idm_team`, `idmteam`,
`employeecomms`, `spamadmin`, `digest`, `calendar-`

### Stage 2 — Subject prefix patterns

Discard if the subject starts with any of (case-insensitive):
- `Accepted:` / `Declined:` / `Tentative:` — calendar responses
- `Invitation:` / `Updated invitation:` / `Cancelled:` — calendar invitations
- `APPROVAL REQUIRED:` — workflow notifications
- `Action Required:` — system action requests
- `Reminder:` — automated reminders
- `Digest:` / `Quarantined` — automated summaries

### Stage 3 — Human judgment

After mechanical filtering, assess each remaining message: does it look like a specific
person wrote this to me, or like a system triggered a notification that happens to carry
a human's name? Discard if:
- The body snippet reads like a template/form (e.g. "has requested access to", "pending
  your approval", "has accepted this invitation")
- It is clearly a mass communication (newsletters, announcements, all-hands invites)

Keep if: a real person appears to be writing something specific to Lanny — a question,
a request, a heads-up, something that warrants a reply.

## Search 1 — Promotion / Focal Requests

Query: `is:unread (promotion OR "focal review" OR calibration OR "provide input" OR "360 feedback") from:@salesforce.com newer_than:7d`

Apply all three filter stages. Present survivors as **Promotion/Focal Requests**.

## Search 2 — Direct Individual Mail

Query: `is:unread to:lripple@salesforce.com from:@salesforce.com newer_than:7d`

Apply all three filter stages. Present survivors as **Direct Mail**.

## Agenda Output

Add a `GMAIL` section to the agenda only if at least one message survives both searches.
List entries as:
```
  [DATE] From: SENDER_NAME — SUBJECT
```

Example:
```
GMAIL
  Promotion/Focal Requests
    [Apr 19] From: Jordan Sarkodie — Re: Promo input for Smriti
  Direct Mail
    [Apr 20] From: Richard Chang — Error arch question
```
