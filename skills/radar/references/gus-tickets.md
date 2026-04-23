# GUS Tickets Procedure

Run this during agenda building when the GUS check reminder fires (Mon/Wed/Fri or
whatever cadence is recorded in the memory file).

## Finding tickets to check

Scan the Notes section of the memory file for entries containing a W-number
(pattern: `W-\d+`) with a monitor cadence (e.g. "Monitor Mon/Wed/Fri").
Collect all such W-numbers.

If no tickets are due today based on their cadence, omit the GUS TICKETS section.

## Querying each ticket

For each W-number, query GUS using the `sfcli:gus` skill:

```
SELECT Name, Subject__c, Status__c, Sprint__r.Name, LastModifiedDate, LastModifiedBy.Name
FROM ADM_Work__c WHERE Name = '{W-NUMBER}'
```

Requires `dangerouslyDisableSandbox: true`.

## Agenda output

Present as a `GUS TICKETS` section. List each ticket with aligned fields:

```
GUS TICKETS
  W-21729767  New        2026.04b-Einstein Infra India
              Last modified: 2026-04-20 by Premdeep Saini
              Terramon migration for prediction-service
```

If status or sprint changed since the last recorded value in Notes, note the change:

```
  W-21729767  In Progress  (was: New)  2026.04b-Einstein Infra India
```

After building the agenda, update the Notes entry in the memory file to reflect
the current status and sprint if they have changed.
