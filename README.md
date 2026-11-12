# Arrival Time Check Agent

A Claude Code sub-agent + skill for hotel operators. It scans upcoming reservations, finds the guests who have not yet given an estimated arrival time, and drafts warm, personalised emails (in the guest's native language) asking for their ETA. By default it **never sends** — every email is a draft for you to review. It can also run on a schedule, and [`AUTONOMY.md`](AUTONOMY.md) sets how much it does when you are not there.

Built on the **WAT framework** (Workflows, Agents, Tools): the AI handles the reasoning and the wording, and your own scripts handle the PMS lookup and the draft creation. This repo is the workflow and the agent. It is markdown only: **the scripts are not included**, you point the agent at the ones your setup has.

---

## What it does

- **Scans the next N days** of arrivals from your PMS (7 by default) and identifies which reservations have no ETA on file
- **Detects the guest's language** from the phone country code (with country-field fallback) so the email is in the guest's own language
- **Shows you the list first** and drafts only after you say yes
- **Drafts a warm, personalised email per guest** — varies wording by length of stay, party size, and check-in day, and uses only facts from the reservation
- **Flags edge cases** for manual handling: OTA relay addresses, guests with no email at all, guests who arrive today or tomorrow, guests who were already asked
- **Optional PMS note** — if you ask, it appends "Arrival time email drafted {date}" to the reservation, which also stops a second request on the next run
- **Runs on its own, within limits you set** — four autonomy levels in [`AUTONOMY.md`](AUTONOMY.md), from "only when I ask" to "send the request yourself, max 5 a day". The default is report only.
- **Remembers what it did** — one entry per run in `runs/LOG.md`, so a guest is not asked twice, and the report starts with what needs you

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

   > Read the README and set this agent up with me. Ask me for each placeholder in the Customising table, one at a time. Then replace the placeholders in `.claude/agents/arrival-time-check.md`, `.claude/skills/arrival-time-check/SKILL.md`, `AUTONOMY.md` and `.claude/settings.example.json`, delete the "Template note" block in the agent and skill files, leave the README and the level in `AUTONOMY.md` as they are, and show me any `{{...}}` that is still open.

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

1. `grep -rn "{{" .claude/ AUTONOMY.md` prints nothing. Every placeholder is filled in.
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
| The same guest is asked again on the next run | `runs/LOG.md` was deleted or the run could not write to it, and no PMS note was written. Keep the log, or ask for the note. |
| A scheduled run does nothing | `AUTONOMY.md` says `Level: PAUSED` or `Level: 0`, the `Level:` line is missing or has an unknown value, or a placeholder is still open. The reason is in the last entry of `runs/LOG.md`. |
| A scheduled run reports "permission denied" for your lookup or draft command | The command does not match an `allow` rule in `.claude/settings.local.json`. Make the rule match the command the skill runs. |
| "send-guard: blocked ..." | The hook stopped a send, reply or forward command. This is correct below Level 3. |
| The language is wrong for a guest | Tell the agent the right one before you confirm. It saves the correction to its memory. |

---

## File structure

```
arrival-time-check-agent/
├── README.md                                         # This file
├── AUTONOMY.md                                       # Autonomy level, limits and guard rails (you edit it)
├── .env.example                                      # Optional record of your setup values
├── .gitignore
├── LICENSE
├── runs/
│   ├── .gitkeep
│   └── README.md                                     # Format of the run log (LOG.md itself is git-ignored)
└── .claude/
    ├── settings.example.json                         # Example permissions + hook for unattended runs
    ├── hooks/
    │   └── send-guard.py                             # Blocks send commands unless AUTONOMY.md allows them
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

The agent and skill files, `AUTONOMY.md` and `.claude/settings.example.json` use placeholders so they can be adapted to any PMS + email stack. Replace the following before first run:

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

## Run it on its own

The agent can run on a schedule with nobody in the conversation. [`AUTONOMY.md`](AUTONOMY.md) decides what such a run can do. Read it once; it is short.

| Level | A scheduled run |
|---|---|
| PAUSED | does nothing and logs why (the kill switch; also applies when the `Level:` line is missing or unknown) |
| 0 | does nothing (the agent works only when you ask) |
| 1 (default) | reports who has no arrival time; creates no drafts |
| 2 | also puts the drafts in your mailbox for you to send |
| 3 | also sends the first request itself (max 5 a day, direct addresses, approved languages, send hours) and adds the PMS note |

Never on its own, at any level: reminders, replies, guests who arrive today or tomorrow, guests whose notes mention a complaint, payment, medical, legal or safety matter, any other PMS write, anything with money, deleting anything. The full table is in `AUTONOMY.md`.

### 1. Permissions for unattended runs

A scheduled run cannot ask you for permission, so the commands it needs must be allowed in advance. [`.claude/settings.example.json`](.claude/settings.example.json) is an example. It is not loaded under that name, so cloning this repo changes nothing. To use it:

```bash
cp .claude/settings.example.json .claude/settings.local.json
```

(`settings.local.json` is git-ignored.) Then make the two `Bash(...)` allow rules match the commands that the skill runs in steps 1 and 5. The example allows: reading files, your lookup command, your draft-create command, and writing to `runs/` and the agent's memory folder. It denies: reading `.env`, editing `AUTONOMY.md`, the settings files and the hook, `rm`, `curl`, `wget`, `git push`, web fetch and web search. Deny rules win over allow rules. Bash rules match the command text as written, so they are a guard rail and not a security boundary; the allowlist is the main control.

For Level 3, add your own send command and `Bash({{PMS_NOTES_TOOL}} *)` to `allow` yourself. They are not in the example on purpose.

### 2. The send guard (hook)

The example settings also register [`.claude/hooks/send-guard.py`](.claude/hooks/send-guard.py) as a `PreToolUse` hook on the Bash tool. It blocks any command that has `send`, `reply` or `forward` as a command word unless `AUTONOMY.md` has the one line `Level: 3` and a `Send command`. It needs `python3`. It applies in normal conversations too, once the settings file is in place. It does not see a send that is hidden inside one of your own scripts, so do not allow a script that sends.

Test it by hand (the first prints nothing and exits 0, the second prints the block reason and exits 2):

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"your-mail-cli draft create --to a@example.com"}}' | CLAUDE_PROJECT_DIR=. python3 .claude/hooks/send-guard.py; echo $?
echo '{"tool_name":"Bash","tool_input":{"command":"your-mail-cli draft send --id 1"}}' | CLAUDE_PROJECT_DIR=. python3 .claude/hooks/send-guard.py; echo $?
```

### 3. The scheduled command

```bash
cd /path/to/arrival-time-check-agent && \
claude -p "/arrival-time-check 7 scheduled" \
  --permission-mode dontAsk \
  --max-turns 30 \
  < /dev/null >> runs/cron.log 2>&1
```

- `-p` runs Claude Code without the interactive screen and prints the report. `/arrival-time-check` runs the skill; the word `scheduled` tells it that nobody can answer questions.
- `--permission-mode dontAsk` denies every tool call that would need a prompt. Only your `allow` rules run.
- `--max-turns` stops a run that goes in circles.
- `< /dev/null` tells Claude Code not to wait for piped input.
- Do not add `--bare`: it skips the skill, the settings and the hook.

Example schedule with cron (macOS or Linux), every day at 07:30. Use the full path that `which claude` prints, because cron has a short `PATH`:

```cron
30 7 * * * cd /path/to/arrival-time-check-agent && /full/path/to/claude -p "/arrival-time-check 7 scheduled" --permission-mode dontAsk --max-turns 30 < /dev/null >> runs/cron.log 2>&1
```

This is an example. The computer must be on, and Claude Code must be logged in for the user that owns the cron job; test the command in a terminal first, then check `runs/cron.log` after the first scheduled run. Claude Code also has its own scheduling features; see [scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) and [desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks) in the docs. We have not tested this agent with them.

A note on plans: the usage limits of a personal Pro or Max plan assume ordinary individual use and fall under Anthropic's usage policy, so for a heavy or business-critical schedule use an API key or a team plan.

### 4. Move up one level at a time

1. Run at the current level for 7 days.
2. Read `runs/LOG.md`. Check that "Needs you" was right, that the "Proposed" lines are what you would have done yourself, and that there are no errors.
3. Change one line in `AUTONOMY.md` (`Level: 2`). The first 5 actions at the new level are shadow-only: the log says "would have drafted" and nothing more happens.
4. Before Level 3: set `Send command`, add the two allow rules, and keep the approved languages to the ones you have read drafts in.

To stop everything, set `Level: PAUSED`. It takes effect at the start of the next run.

### What it hands to other agents

- `runs/LOG.md` — one entry per run. [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) can read the latest entry and the level in `AUTONOMY.md` for the daily briefing.
- `runs/handoff/arrival-time-check-agent.md` — the current state of each reservation without an arrival time (asked, sent, manual follow-up). [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) can use it to recognise a guest's answer.

The formats are in [`runs/README.md`](runs/README.md).

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
- [`agent-notification-agent`](https://github.com/th1-ai/agent-notification-agent) — can tell you when a scheduled run has something under "Needs you"

All 21 agents: [th1.ai/agent-stack](https://th1.ai/agent-stack)

---

## License

MIT — see [LICENSE](LICENSE).
