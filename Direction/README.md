# Direction

**Tier 3 — constant input.** Loaded at the start of every session, together with
`Objectives.md`. One file per area, plus trigger-loaded lenses. Written **only in
review**, always with provenance.

## `Direction/<area>.md`

| Section | Horizon | Test |
|---|---|---|
| `## Purpose` | H5 | Why this area exists. One paragraph, ≤5 lines. Rarely changes. |
| `## Principles` | H5 | Standing constraints. Cannot be failed — they are not targets. |
| `## Standards` | H2 | What "well-maintained" means. No finish line, but a quality bar. |

No other `##` sections are permitted — `lint_vault.py` enforces this.

**Item shape:** every principle and standard is **one line**, carries a stable ID
(`P1`, `S2`, …) and an adopted date, with a source link when promoted from
evidence:

```markdown
- P1 — <one line> (adopted YYYY-MM-DD — [[source]])
```

IDs are stable so objectives, syntheses, and review logs can cite `P2`/`S1`
instead of paraphrasing. **Whole-file cap:** `LEXICON_DIRECTION_CAP` lines
(default 60) — adding an eighth principle puts the other seven on screen; the cap
is the retirement forcing function. Operational detail (workflows, file shapes,
tooling) belongs in `docs/` and rules, never here.

## `Direction/Lenses/<name>.md`

A **lens** is a runnable protocol — a decision process or evaluation procedure —
too big for a one-line item but normative in use. Review-owned, but
**trigger-loaded, not constant-loaded**: a one-line Standard points at it, and the
lens's own `## When to run this` section is the trigger.

Required sections: `## When to run this`, `## Process`, `## Failure-mode guards`.
Cap: `LEXICON_LENS_CAP` lines (default 220). Build path: iterate the draft in
`Sources/Ideas/`, promote the final version in a review session, retire the
superseded drafts.

## The membership test

> No finish line, can't be failed → **Principle** (`Direction/<area>.md`)
> No finish line, but has a quality bar → **Standard** (`Direction/<area>.md`)
> Has a date and can be missed → **Objective** (`Objectives.md`)
> Has a deliverable → it's a **Project** — it does not live in this vault
> Runnable procedure, no finish line, too big for one line → **Lens** (`Direction/Lenses/`), pointed at by a Standard

Horizon-bound intentions (H3) live in the root `Objectives.md`, not here, so the
cap across all areas stays visible in one place. Projects (H1) and next actions
do not live in this vault at all.

`Sources/`, `Evidence/` and `Synthesis/` are the **descriptive** tiers: what
happened, what was said, what it adds up to. This directory is what you intend —
see [docs/MEMORY_MODEL.md](../docs/MEMORY_MODEL.md) and
[docs/OBJECTIVES.md](../docs/OBJECTIVES.md).
