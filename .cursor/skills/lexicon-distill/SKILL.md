---
name: lexicon-distill
description: Extract important statements from a meeting note into Memory and People evidence only — never # Current model. Use when user says "distill this meeting note". Not used in triage.
---

# Distill meeting note into memory

Appends **evidence only** from a meeting note. **Triage** later updates `# Current model` from that evidence.

**Rule:** `.cursor/rules/distill.mdc`

## Hard boundaries

**Never during distill:**
- `# Current model` on Memory area files
- `# Current read` on People pages
- `Direction.md`
- `triaged` on meeting notes

**Do append:**
- Memory `# Evidence` (Product, Org, Validation, Partners, **Me**)
- People `# Evidence Log`
- `## Open decisions` / `## Open hypotheses` when meeting records pending items
- Classic topic slugs: `Product/<topic>.md`, `Decisions/decisions.md` — only when the project has no area files
- AI Evaluation → `Me.md` `# Evidence` when it exists; `Personal/ai_evaluation.md` only in classic layout

## Prerequisites

Meeting note under `Meetings/<Project>/`.

## Steps

1. **Read the meeting note** — Signals, Decisions, Action Items, Summary, Context.
2. **Detect memory layout** — Area files if `Memory/<Project>/Product.md` (or `Me.md`) exists at root; else topic slugs. See distill rule.
3. **Apply distill rule** — Append evidence only.
4. **Fill `# Distilled`** on the meeting note — list files touched.
5. **Reply** — Confirm files updated.

## Error handling

- **No meeting note** — Ask which note.
- **No project** — Ask which project.
- **Append-only** — Never overwrite past evidence entries.
