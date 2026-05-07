---
name: Detect language from phone country code first, country field second
description: Phone-prefix language detection beats nationality-field detection because the phone is what the guest actually uses
type: feedback
---

> **Example pattern.** This file shows the *shape* of a useful agent-memory note. Replace it with your own learnings as the agent runs.

When detecting which language to write the arrival-time email in, the phone country code is a stronger signal than the nationality / country field on the reservation. Reasons:

- A French guest living in London will often have a +44 number — they want the email in English (their day-to-day language), not French.
- A German guest visiting from Belgium may have `country = BE` in the PMS but a `+49` phone — German is the right choice.
- OTA relay phone numbers are usually preserved on the booking even when the relay email hides the address.

**How to apply:**

1. Try phone country code first. Map +33 → French, +39 → Italian, +49 → German, etc.
2. Fall back to the `guestCountry` / nationality field only if the phone is missing.
3. For ambiguous prefixes (+32 Belgium, +41 Switzerland) use the country field to disambiguate French vs Dutch / French vs German / French vs Italian.
4. Default to English when neither resolves.
5. Always show the chosen language in the summary table so the operator can override before drafting.

**Anti-pattern to avoid:** assuming nationality determines language. Many guests live abroad. Phone is the better proxy for "what language does this person live in day to day".
