---
name: arrival-time-check
---

# Skill: Arrival Time Check

Check upcoming arrivals for missing estimated arrival times and draft emails to guests asking for their ETA.

## Trigger

User says "arrival time check", "check arrival times", "weekly arrivals", "who hasn't told us their arrival time", or similar.

> **Template note:** Replace `{{HOTEL_NAME}}`, `{{OPERATOR_NAME}}`, `{{INBOX_*}}`, `{{EMAIL_CLI}}`, `{{PMS_LOOKUP_TOOL}}` and `{{PMS_NOTES_TOOL}}` with the wrappers your setup uses. See [README.md](../../../README.md#customising) for guidance.

## Process

### 1. Fetch reservations and check arrival times

```bash
{{PMS_LOOKUP_TOOL}} --days 7 --format json
```

Parse the JSON output. Present a summary:

```
### Arrival Time Check — {from_date} to {to_date}

**{total} arrivals** | {with_arrival_time} have arrival times | {missing} missing

#### Missing arrival times:
- **<Guest>** — checking in {date}, <RoomType> ({email}) [OTA relay / NO EMAIL if applicable]

#### Already have arrival times:
- **<Guest>** — checking in {date}, arriving {time} (source: {source})
```

### 2. Detect guest language from phone country code

For each guest missing an arrival time, fetch the full reservation to get the guest's phone number and country (the `{{PMS_LOOKUP_TOOL}}` should ideally return these directly so you don't need a second call).

Determine the guest's preferred language from the phone country code:

| Phone prefix | Country | Email language |
|-------------|---------|---------------|
| +33 | France | French |
| +39 | Italy | Italian |
| +34 | Spain | Spanish |
| +49 | Germany | German |
| +31 | Netherlands | Dutch |
| +32 | Belgium | French (default) or Dutch — use guestCountry to disambiguate |
| +41 | Switzerland | French (default) — use guestCountry to disambiguate |
| +82 | South Korea | Korean |
| +81 | Japan | Japanese |
| +86 | China | Chinese |
| +7 | Russia | Russian |
| +351 | Portugal | Portuguese |
| All others (+44, +1, +61, etc.) | English-speaking or unknown | English |

**Rules:**
- Phone country code is the primary signal. If no phone number, fall back to `guestCountry` field.
- If both are missing, default to English.
- Include the detected language in the summary table shown to the operator.

Present the summary with language column:

```
#### Missing arrival times:
| Guest | Check-in | Room | Phone | Language | Email |
|-------|----------|------|-------|----------|-------|
| <Guest> | {date} | <RoomType> | {phone} | {language} | {email_type} |
```

### 3. Confirm before drafting

Ask:
- "Shall I draft arrival time emails for the {N} guests above?"
- "Which account should I send from?" (default: `{{INBOX_BOOKINGS}}`)
- Check if any guests should be skipped (e.g. arriving with another guest, or already in conversation).

Flag separately:
- **Missing emails** — no email on file, flag for manual follow-up.

Note: OTA relay emails (e.g. `@guest.booking.com`) work fine — they forward to the guest. Treat them the same as direct emails.

**Do NOT draft emails without confirmation.**

### 4. Draft emails for each flagged guest

For each guest with a usable email and missing arrival time, create a draft:

```bash
{{EMAIL_CLI}} draft create \
  --account {{INBOX_BOOKINGS}} \
  --to "{guest_email}" \
  --subject "Your upcoming stay at {{HOTEL_NAME}}" \
  --body '{html_body}' \
  --html
```

#### Email guidelines

**Tone:** Warm, personal, brief. Use the guest's first name. Mention their check-in date. Must NOT sound like an automated system.

**CRITICAL: Write each email in the guest's detected language.** The subject line must also be in the guest's language. Maintain the same warm, personal tone regardless of language — do not fall back to overly formal phrasing just because it is a foreign language.

**Structure:**
1. Opening — express that we're looking forward to welcoming them
2. Request — ask for approximate arrival time, explain why (room preparation, key arrangements for late arrivals)
3. Offer — invite questions about getting here or anything else
4. Sign-off — "Best regards, {{OPERATOR_NAME}}, {{HOTEL_NAME}}"

**CRITICAL: Vary the wording for each guest.** Do NOT send identical emails. Adapt based on:
- Length of stay (weekend vs. week-long)
- Party size ("you and your family" if children present, "you and your group" for multiple adults)
- Room type (only if noteworthy)
- Check-in day (Friday evening vs. Monday midday → different context)

**Phrases to NEVER use:**
- "Thank you for reaching out"
- "I hope this email finds you well"
- "This is an automated reminder"
- "As per our policy"
- "Dear Sir/Madam"
- "We regret to inform you"

**Example tone (do not copy verbatim — adapt for each guest):**

```html
<p>Dear {first_name},</p>

<p>We're looking forward to welcoming you on {check_in_date}.</p>

<p>Could you let us know roughly what time you're expecting to arrive? It helps us make sure everything is ready for you, rooms freshened up, and if you're arriving later in the evening we can leave keys and instructions somewhere convenient.</p>

<p>If you have any questions about getting here or anything else before your stay, don't hesitate to ask.</p>

<p>Best regards,<br>
{{OPERATOR_NAME}}<br>
{{HOTEL_NAME}}</p>
```

### 5. Report results

After drafting, present:

```
### Drafts Created

- **<Guest>** — draft in bookings inbox (Draft ID: {id})
- ...

{N} drafts ready for review in {{INBOX_BOOKINGS}} → Drafts.
```

If any guests had missing emails, flag:
- "**<Guest>** has no email on file — follow up manually"

### 6. Optionally log to PMS

If the operator confirms, add a note to each reservation:

```bash
{{PMS_NOTES_TOOL}} \
  --reservation-id <RES_ID> \
  --note "Arrival time email sent {date}"
```

## Guardrails

- **NEVER send emails** — only create drafts
- **ALWAYS confirm** before drafting
- **ALWAYS use HTML** — never plain text
- **Emails must be warm and personal** — never corporate or templated
- **ALWAYS detect guest language** from phone country code before drafting — write emails in the guest's language
- **Never oversell** — don't describe the property in the email, just be helpful
