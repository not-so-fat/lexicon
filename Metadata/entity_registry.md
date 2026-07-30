# Entity registry

Canonical names for people, companies, and products. Transcripts regularly
mis-hear entity names; **summarize** and **distill** normalize against this
file so meeting notes, evidence bullets, and `People/` routing always use one
spelling per entity.

**Inclusion criteria (lean by design):** recurring relationships only — team
members, active partners, mentors. Never interview candidates, and never
someone met once or twice; they enter via `## Proposed` if they recur.

Format: `- **Canonical Name** (person|company|product, <relationship>[ — role]) — aliases: <comma-separated mis-hearings>`

## Canonical

Human-approved only — agents never add here directly. New entities and aliases
enter through `## Proposed` and are approved in a **triage** session.

<!--
- **Ada Lovelace** (person, team — engineering) — aliases: Ada Loveless, Ada Lovelance
- **Acme Corp** (company, partner) — aliases: Acme Core, Acme Co
-->

## Proposed (review at triage)

Appended by summarize/distill when they meet an unrecognized name or a
suspected mis-hearing (dated, with the source note). Triage resolves each with
the user: approve → move to `## Canonical` (as entity or alias, with a
relationship attribute), or reject → delete the line.

<!--
- YYYY-MM-DD — **Heard Name** (person?) — likely <new entity | alias of **Canonical**>; heard in [[Sources/Meetings/<area>/<note>]]
-->
