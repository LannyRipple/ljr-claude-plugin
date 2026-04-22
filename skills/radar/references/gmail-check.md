# Gmail Check Procedure

Run this during agenda building. Use `mcp__plugin_gmail_gmail__gmail_search` for both
searches. Fetch subject, sender, and date only — do not retrieve full bodies.

## Automated Sender Filter

After each search, discard results where the sender address contains any of:
`noreply`, `no-reply`, `donotreply`, `do-not-reply`, `notification`, `automated`,
`workday`, `servicenow`, `mailer-daemon`, `postmaster`

## Search 1 — Promotion / Focal Requests

Query: `is:unread (promotion OR "focal review" OR calibration OR "provide input" OR "360 feedback") from:@salesforce.com newer_than:7d`

After filtering automated senders, present surviving results as **Promotion/Focal Requests**.

## Search 2 — Direct Individual Mail

Query: `is:unread to:lripple@salesforce.com from:@salesforce.com newer_than:7d`

After filtering automated senders, present surviving results as **Direct Mail**.

## Agenda Output

Add a `GMAIL` section to the agenda. For each non-empty category, list entries as:
```
  [DATE] From: SENDER_NAME — SUBJECT
```

If both categories are empty, omit the GMAIL section entirely.

Example:
```
GMAIL
  Promotion/Focal Requests
    [Apr 19] From: Jordan Sarkodie — Re: Promo input for Smriti
  Direct Mail
    [Apr 20] From: Richard Chang — Error arch question
```
