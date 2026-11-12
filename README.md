# Arrival Time Check Agent

A Claude Code sub-agent + skill for hotel operators. It scans upcoming reservations, finds the guests who have not yet given an estimated arrival time, and drafts warm, personalised emails (in the guest's native language) asking for their ETA. It **never sends** — every email is a draft for you to review.

Built on the **WAT framework** (Workflows, Agents, Tools): the AI handles the reasoning and the wording, and your own scripts handle the PMS lookup and the draft creation. This repo is the workflow and the agent. It is markdown only: **the scripts are not included**, you point the agent at the ones your setup has.

---

## What it does

- **Scans the next N days** of arrivals from your PMS (7 by default) and identifies which reservations have no ETA on file
- **Detects the guest's language** from the phone country code (with country-field fallback) so the email is in the guest's own language
- **Shows you the list first** and drafts only after you say yes
- **Drafts a warm, personalised email per guest** — varies wording by length of stay, party size, and check-in day, and uses only facts from the reservation
- **Flags edge cases** for manual handling: OTA relay addresses, guests with no email at all, guests who arrive today or tomorrow, guests who were already asked
- **Optional PMS note** — if you ask, it appends "Arrival time email drafted {date}" to the reservation, which also stops a second request on the next run

---

## What you need

- [Claude Code](https://code.claude.com/docs/en/quickstart) installed
- A PMS with API access, and a script that returns a JSON list of upcoming reservations with their arrival-time fields. Any PMS with reservation lookup + an estimated-arrival-time field works. The fields the agent expects are listed in step 1 of the [skill](.claude/skills/arrival-time-check/SKILL.md).
- A command-line tool that can create email drafts in your mailbox (for example a Google Workspace CLI for Gmail)
- Optional: a script that appends a note to a reservation

---

## Quick start

1. **Clone the repo** and open Claude Code in it:

   ```bash
   git clone https://github.com/th1-ai/arrival-time-check-agent.git
   cd arrival-time-check-agent
   claude
   ```

2. **Let Claude set it up with you.** Paste this:

   > Read the README and set this agent up with me. Ask me for each placeholder in the Customising table, one at a time. Then replace the placeholders in `.claude/agents/arrival-time-check.md` and `.claude/skills/arrival-time-check/SKILL.md`, delete the "Template note" block in both files, leave the README as it is, and show me any `{{...}}` that is still open.

   Or do it by hand: edit [`.claude/agents/arrival-time-check.md`](.claude/agents/arrival-time-check.md) and [`.claude/skills/arrival-time-check/SKILL.md`](.claude/skills/arrival-time-check/SKILL.md) and replace the placeholders described in [Customising](#customising).

3. **Adapt the two example commands** in the skill (steps 1 and 5) to the flags your own scripts take. The ones in the file are examples.

4. **Check it** — see [Verify it works](#verify-it-works).

5. **Invoke the agent**:

   > "Run the arrival time check for the next 7 days."

   Claude Code delegates to the `arrival-time-check` sub-agent because of its `description` line. To be explicit, type `@agent-arrival-time-check` in your message, or run the skill in the main conversation with `/arrival-time-check`.

   The sub-agent comes back with the list of guests and asks which ones to draft for. Answer in the conversation, and Claude sends it back to create the drafts.

`.env.example` is optional. Claude Code does not load it; it is there as a record of your setup values and for credentials that your own scripts need. If you use it, `cp .env.example .env` (`.env` is git-ignored).

---

## Verify it works

1. `grep -rn "{{" .claude/` prints nothing. Every placeholder is filled in.
2. `/agents` in Claude Code lists `arrival-time-check`, and typing `/` shows the `arrival-time-check` skill. If you added the files while Claude Code was open and the agent is not listed, restart Claude Code.
3. Your lookup script runs by itself in a terminal and prints JSON.
4. Ask: "Run the arrival time check, scan only, no drafts." You get the summary table and no drafts in your mailbox.
5. Confirm one guest, then open the draft in your mailbox: right inbox, right language, your name in the sign-off, not sent.

### Troubleshooting

| What you see | Likely cause |
|---|---|
| The agent stops and lists `{{...}}` names | Placeholders are not all replaced. Run check 1. |
| "Lookup tool failed" with no table | Your script printed an error and no JSON. Run it by hand to see the error. |
| A draft is cut off or the command fails on some guests | An apostrophe in the email body broke the shell quoting. Let your wrapper read the body from a file or stdin. |
| The same guest is asked again on the next run | No PMS note was written. Ask for the note after you send, or tell the agent who to skip. |
| The language is wrong for a guest | Tell the agent the right one before you confirm. It saves the correction to its memory. |

---

## File structure

```
arrival-time-check-agent/
├── README.md                                         # This file
├── .env.example                                      # Optional record of your setup values
├── .gitignore
├── LICENSE
└── .claude/
    ├── agents/
    │   └── arrival-time-check.md                     # Sub-agent definition (preloads the skill)
    ├── skills/
    │   └── arrival-time-check/
    │       └── SKILL.md                              # Skill (full process and email rules)
    └── agent-memory/
        └── arrival-time-check/
            ├── MEMORY.md                             # Index the agent reads on each run
            └── example-feedback-pattern.md           # Example "memory note" — replace with your own
```

---

## Customising

The agent and skill files use placeholders so they can be adapted to any PMS + email stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{HOTEL_NAME}}` | Hotel display name (used in email sign-off) | `The Garden Inn` |
| `{{OPERATOR_NAME}}` | Sender name (used in email sign-off) | `Alex Morgan` |
| `{{INBOX_BOOKINGS}}` | Inbox the drafts are created in by default | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property / villa inbox. If you have none, use the same address as above | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Command that can create email drafts | `gws gmail` |
| `{{PMS_LOOKUP_TOOL}}` | Script that lists upcoming reservations + ETA fields | `tools/check_arrival_times.py` |
| `{{PMS_NOTES_TOOL}}` | Script that appends a note to a reservation. If you have none, write `not available` and do not ask for PMS notes | `tools/pms_notes.py` |

The script names in the examples are placeholders for your own scripts. The language table, the banned phrases and the house spelling (British English by default) are in the skill file; edit them there.

---

## How memory works

The agent uses Claude Code's per-agent memory (`memory: project`) at `.claude/agent-memory/arrival-time-check/`. Claude Code loads `MEMORY.md` from that folder into the agent on each run, and the agent can save notes there, for example:

- **Feedback** — patterns that improve future drafts (e.g. "Belgian +32 numbers — ask which language before drafting")
- **Project notes** — local context that affects the email (e.g. "weekend trains from {nearest city} arrive late on Friday — adjust late-arrival framing")
- **References** — pointers to other systems (e.g. "follow-up cadence lives in the pre-arrival-outreach agent")

[`example-feedback-pattern.md`](.claude/agent-memory/arrival-time-check/example-feedback-pattern.md) shows the recommended format. Delete it (and its line in `MEMORY.md`) once you have your own. The folder is in git, so do not let guest names or contact details into the notes.

---

## Related agents

This agent works well alongside:

- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent) — drafts the longer pre-arrival welcome message for premium bookings; that message also asks for the arrival time, so skip those guests here
- [`concierge-agent`](https://github.com/th1-ai/concierge-agent) — handles the dining / transfer / activity questions guests reply with
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — the daily briefing; a natural place to run this check once a week
- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) — picks up the guest's reply and adds the arrival time to the PMS reservation as a note

All 21 agents: [th1.ai/agent-stack](https://th1.ai/agent-stack)

---

## License

MIT — see [LICENSE](LICENSE).
