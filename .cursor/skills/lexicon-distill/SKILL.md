---
name: lexicon-distill
description: Use when the user asks to distill a meeting note ("distill this meeting note", or the distill step of a processing pipeline). Not for triage sessions or Ideas files.
---

# Distill meeting note into evidence

Appends **evidence only** from a meeting note. **Triage** later rewrites
`Synthesis/<area>.md` from that evidence.

**Rule:** `.cursor/rules/distill.mdc`

## Hard boundaries

**Never during distill:**
- `Synthesis/**` (triage's tier)
- `Direction/**`, `Objectives.md` (review's tier)
- `triaged` on meeting notes
- Rewriting or deleting existing evidence bullets — `Evidence/` is append-only and permanent

**Do append (all under `Evidence/<area>/`, create files with the `# Evidence (append-only)` heading if missing):**
- Product / market signals → `Product.md`; cross-partner patterns → `Validation.md`
- Partner-specific → `Partners/<Company>.md`
- Org / process → `Org.md`
- Person observations → `People/<Name>.md`
- AI Evaluation → `Me.md` (one compact line per meeting)
- Decided decisions → routed domain file with `Decision:` prefix; pending → `Pending decision:` prefix (triage promotes them to Synthesis)

**Bullet cap:** one line, ~30 words / 240 chars of claim text (source links and #tags don't count), dated, with source link.
Detail stays in the meeting note — never re-summarize the meeting into the bullet.

**Route by subject:** evidence about another area goes to that area's
`Evidence/` files, wherever the meeting note lives. List cross-area destinations
in `# Distilled`.

## Prerequisites

Meeting note under `Sources/Meetings/<area>/`.

## Steps

1. **Read the meeting note** — Signals, Decisions, Action Items, Summary, Context.
2. **Read registries** — `Metadata/topic_registry.md` for canonical `#topic_slug`
   tags and any `Topics/<slug>.md` routing; `Metadata/entity_registry.md` for
   canonical people/company spellings (People/Partners files always use the
   canonical name; unknowns → dated `## Proposed` line, never `## Canonical`);
   missing registries → best-effort.
3. **Apply the distill rule** — Follow `.cursor/rules/distill.mdc` in full.
   Inline `#topic_slug` when a bullet also relates to a registered topic.
4. **Fill `# Distilled`** — list every file you updated in the meeting note.
5. **Lint gate (mandatory)** — run:
   ```bash
   python3 scripts/lint_vault.py --files <every file you touched>
   ```
   Fix every error before finishing. A distill that leaves lint errors is not done.
6. **Reply** — confirm done, list updated files and the lint result.

## Error handling

- **No meeting note** — ask which note to distill.
- **Note has no area** — ask which area (check `Metadata/area_registry.md`).
- **Append-only** — never overwrite past entries; a clearly wrong past bullet gets
  a dated correction appended, not an edit.
