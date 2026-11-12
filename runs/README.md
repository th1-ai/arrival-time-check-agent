# Run log

The agent appends one entry to `runs/LOG.md` at the end of every run, and reads the recent entries at the start of the next one. This is how it knows which reservations it already drafted or sent an email for.

Everything in this folder except this file is git-ignored. The entries hold reservation IDs and draft IDs only. Do not put guest names, email addresses or phone numbers here.

## Entry format

Newest entry last. One entry per run:

```
## 2026-01-12T07:30 | Level 2 | scheduled
- Checked: 14 arrivals, 2026-01-12 to 2026-01-19, 5 without an arrival time
- Done: drafted R-1001 (draft d-88), drafted R-1002 (draft d-89)
- Shadow: none
- Proposed: none
- Errors: none
- Needs you: R-1003 no email on file; R-1004 arrives tomorrow
```

- The heading is the local time, the level the run worked at, and `scheduled` or `on request`.
- `Done` lists every write with its ID: `drafted`, `sent`, `noted`.
- `Shadow` lists what the run would have done under the shadow-first rule: `would have drafted R-1005`.
- `Proposed` lists work that needs a higher level or your yes.
- A run that stopped early says why on the `Errors` line.

## Handoff file

`runs/handoff/arrival-time-check-agent.md` is rewritten on every run. It is the current state, for you and for the sibling agents ([`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) reads it for the daily briefing; [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) can use it to recognise a guest's answer):

```
# Arrival times: state at 2026-01-12T07:30
| Reservation | Check-in | State |
|---|---|---|
| R-1001 | 2026-01-15 | asked (draft d-88, not sent) |
| R-1003 | 2026-01-14 | manual follow-up: no email |
| R-1004 | 2026-01-13 | manual follow-up: arrives tomorrow |
```

States: `asked (draft ..., not sent)`, `asked (sent)`, `manual follow-up: {reason}`, `not asked: {reason}`.
