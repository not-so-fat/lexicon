# Entity registry

Canonical names for people, companies, and products. Transcripts regularly
mis-hear entity names; **summarize** and **distill** normalize against this
file so meeting notes, evidence bullets, and `People/` routing always use one
spelling per entity.

Format: `- **Canonical Name** (person|company|product) — aliases: <comma-separated mis-hearings/variants>`

## Canonical

Human-approved only — agents never add here directly. New entities and aliases
enter through `## Proposed` and are approved in a **triage** session.

<!--
- **Ada Lovelace** (person) — aliases: Ada Loveless, Ada Lovelance
- **Acme Corp** (company) — aliases: Acme Core, Acme Co
-->

## Proposed (review at triage)

Appended by summarize/distill when they meet an unrecognized name or a
suspected mis-hearing (dated, with the source note). Triage resolves each with
the user: approve → move to `## Canonical` (as entity or alias), or reject →
delete the line.

<!--
- YYYY-MM-DD — **Heard Name** (person?) — likely <new entity | alias of **Canonical**>; heard in [[Sources/Meetings/<area>/<note>]]
-->
