# Arrival Time Check Agent

A Claude Code sub-agent + skill for hotel operators. It scans upcoming reservations, finds the guests who have not yet given an estimated arrival time, and drafts warm, personalised emails (in the guest's native language) asking for their ETA. It **never sends** — every email is a draft for you to review.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

---

## What it does

- **Scans the next N days** of arrivals from your PMS and identifies which reservations have no ETA on file
- **Detects the guest's language** from the phone country code (with country-field fallback) so the email is in the guest's own language
- **Drafts a warm, personalised email per guest** — varies wording by length of stay, party size, and check-in day
- **Flags edge cases** for manual handling: OTA-relay-only addresses, guests with no email at all, guests whose request has already been answered
- **Optional PMS note** — if you ask, it appends "Arrival time email sent {date}" to the reservation

---

## What you need

- [Claude Code](https://claude.ai/code) installed
- A PMS with API access — the agent calls a `check_arrival_times`-style script that returns a JSON list of upcoming reservations. The reference setup uses Cloudbeds, but any PMS with reservation lookup + estimated-arrival-time fields works.
- An email account you can read/draft to programmatically (Gmail via the Google Workspace CLI is the reference setup)

---

## Quick start

1. **Clone the repo** into a Claude Code project:

   ```bash
   git clone https://github.com/th1-ai/arrival-time-check-agent.git
   cd arrival-time-check-agent
   ```

2. **Copy the env template** and fill it in:

   ```bash
   cp .env.example .env
   ```

3. **Edit [`.claude/agents/arrival-time-check.md`](.claude/agents/arrival-time-check.md)** and [`.claude/skills/arrival-time-check/SKILL.md`](.claude/skills/arrival-time-check/SKILL.md) — replace the placeholders described in [Customising](#customising) with the wrappers your setup uses.

4. **Open in Claude Code** from the project root:

   ```bash
   claude
   ```

5. **Invoke the agent**:

   > "Run the arrival time check for the next 7 days."

   Claude Code will pick up the `arrival-time-check` sub-agent automatically because of the front-matter `description` line.

---

## File structure

```
arrival-time-check-agent/
├── README.md                                         # This file
├── .env.example
├── .gitignore
├── LICENSE
└── .claude/
    ├── agents/
    │   └── arrival-time-check.md                     # Sub-agent definition
    ├── skills/
    │   └── arrival-time-check/
    │       └── SKILL.md                              # Skill (full process)
    └── agent-memory/
        └── arrival-time-check/
            └── example-feedback-pattern.md           # Example "memory note" — replace with your own
```

---

## Customising

The agent and skill files use placeholders so they can be adapted to any PMS + email stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{HOTEL_NAME}}` | Hotel display name (used in email sign-off) | `The Garden Inn` |
| `{{OPERATOR_NAME}}` | Sender name (used in email sign-off) | `Alex Morgan` |
| `{{INBOX_PRIMARY}}` | Main business inbox | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Inquiries / OTA inbox (default for these drafts) | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property / villa inbox (optional) | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Wrapper that can create Gmail drafts | `gws gmail` |
| `{{PMS_LOOKUP_TOOL}}` | Script that lists upcoming reservations + ETA fields | `tools/check_arrival_times.py` |
| `{{PMS_NOTES_TOOL}}` | Script that appends a note to a reservation (optional) | `tools/pms_notes.py` |

The reference setup uses scripts named `tools/check_arrival_times.py` and `tools/pms_notes.py` — point these at whatever your PMS exposes.

---

## How memory works

The agent uses Claude Code's per-agent memory at `.claude/agent-memory/arrival-time-check/`. After each run, it can save:

- **Feedback** — patterns that improve future drafts (e.g. "Belgian +32 numbers — disambiguate FR vs NL via guest country")
- **Project notes** — local context that affects the email (e.g. "weekend trains from {nearest city} arrive late on Friday — adjust late-arrival framing")
- **References** — pointers to other systems (e.g. "follow-up cadence lives in the pre-arrival-outreach agent")

[`example-feedback-pattern.md`](.claude/agent-memory/arrival-time-check/example-feedback-pattern.md) shows the recommended format. Delete it once you have your own.

---

## Related agents

This agent works well alongside:

- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent) — once the ETA is known, this drafts the warmer pre-arrival welcome message and any concierge offers
- [`concierge-agent`](https://github.com/th1-ai/concierge-agent) — handles the dining / transfer / activity questions guests reply with
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — calls this agent on Mondays as part of the weekly briefing
- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) — catches the guest's ETA reply and routes it back to the PMS

---

## License

MIT — see [LICENSE](LICENSE).
