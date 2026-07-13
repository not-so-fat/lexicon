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
- Memory evidence files — area layout: `<Area>.evidence.md` siblings (Product, Org, Validation, Partners, **Me**); create if missing, never write evidence into the model file
- People `# Evidence Log`
- `## Open decisions` / `## Open hypotheses` when meeting records pending items (the only model-file write)
- Classic topic slugs: `Product/<topic>.md`, `Decisions/decisions.md` — only when the project has no area files
- AI Evaluation → `Me.evidence.md` when `Me.md` exists; `Personal/ai_evaluation.md` only in classic layout

**Bullet cap:** one line, ~30 words max, dated, with meeting-note source link. Detail stays in the meeting note — never re-summarize the meeting into the evidence line.

**Route by subject:** evidence about another project goes to that project's Memory files, wherever the meeting note lives. List cross-project destinations in `# Distilled`.

**Not triage.** Distill appends **evidence** only. Synthesis (`# Current model`, `# Current read`, Direction) happens in **lexicon-triage** after user approval. See `Memory/Lexicon/processing-strategy.md`.

## Prerequisites

Meeting note under `Meetings/<Project>/`.

## Steps

1. **Read the meeting note** — Signals, Decisions, Action Items, Summary, Context.
2. **Detect memory layout** — Area files if `Memory/<Project>/Product.md` (or `Me.md`) exists at root; else topic slugs. See distill rule.
3. **Read registries** — Read `Metadata/topic_registry.md` (for topic matching); classic layout: list existing files under `Memory/<Project>/Product/` and `Org/` (match-before-create). If registries or folders are missing, proceed with best-effort matching.
4. **Apply distill rule** — Follow `.cursor/rules/distill.mdc` in full. Key additions:
   - **Topic matching**: before creating a new Memory topic file, check the topic registry for canonical slugs and aliases. Use existing topics when possible. Add genuinely new topics to the registry.
   - **Inline `#topic`**: when writing a bullet to a Memory or People page, append `#topic_slug` if the fact also relates to another registered topic.
   - **Relationships**: when signals reveal interpersonal dynamics, update the `# Relationships` section on **both** people's pages.
5. **Fill `# Distilled`** — In the meeting note, list every file you updated.
6. **Reply** — Confirm done and list updated files.

## Error handling

- **No meeting note** — Ask user which note to distill.
- **Note has no project** — Ask user which project (check `Metadata/project_registry.md` when available).
- **Append-only** — Never overwrite past entries in People or Memory; always append.
- **No synthesis** — Do not edit `# Current model`, `# Current read`, or `Direction.md`. Do not set `triaged` on meeting notes.
