# Lexicon Memory Model

How Lexicon organizes knowledge, and how the directory tree enforces it.

**Pipeline:** Ingest → Summarize → **Distill** (evidence) → **Triage** (synthesis) → **Review** (direction & objectives) → Query

---

## The tiers ARE the directories

Knowledge is split by **how the agent consumes it**, and each tier is a top-level
directory with one mutation contract. Every rule below is derivable from the path —
no filename conventions, no layout detection, no hand-maintained maps.

| Tier | Directory | Contract | Maintained by |
|---|---|---|---|
| **1. Sources** | `Sources/` | Write-once captures. Never edited after distill (except traceability stamps). | Ingest + summarize |
| **2. Evidence** | `Evidence/` | Append-only dated one-line pointers into Sources. Permanent — never compacted. | Distill (lint-gated) |
| **2.5 Synthesis** | `Synthesis/` | What the evidence adds up to. **Rewritten wholesale** at each triage; plus per-decision state files. | Triage (human-in-loop) |
| **3. Constant input** | `Direction/` + `Objectives.md` | Small, curated, loaded every session. Lenses load by trigger. | Review (human-approved) |
| — | `Metadata/` | Engine state: registries, recap/review logs, usage telemetry. | Scripts + sessions |

Agents read **top-down** for truth questions: Direction → Synthesis → Evidence → Sources.
For intent questions ("what am I trying to do") read `Objectives.md` first — see
[OBJECTIVES.md](OBJECTIVES.md).

```
Sources/                      # Tier 1 — write-once
  Meetings/<area>/…
  Transcripts/…
  Ideas/<area>/…              #   editable until triaged, then promoted or deleted
  Clippings/
Evidence/                     # Tier 2 — append-only, dated one-liners
  <area>/
    Product.md  Org.md  Me.md  Validation.md
    Partners/<Company>.md
    People/<Name>.md
    Topics/<slug>.md          #   optional, same contract, slug from registry
Synthesis/                    # Tier 2.5 — rewritten each triage
  <area>.md
  <area>/decisions/<slug>.md  #   per-decision state files
  <area>/people/<Name>.md     #   per-person current reads (refreshed at triage)
  <area>/partners/<Co>.md     #   per-partner current reads (refreshed at triage)
Direction/                    # Tier 3 — constant input, review-owned
  <area>.md
  Lenses/<name>.md            #   runnable protocols, trigger-loaded
Objectives.md                 # Tier 3 — root by design; first file every session reads
Metadata/
```

---

## Tier 1 — Sources

Meeting notes, transcripts, ideas, clippings. Rich capture, generous summarize.

- Meeting notes are **never edited after distill**, except the `# Distilled`
  traceability section.
- Ideas/Clippings are working captures: editable until triaged, then **promoted or
  deleted** (git preserves history). Nothing lives in `Sources/Ideas/` permanently.
- Every file carries frontmatter (`area:`, `created:`, …) — files without it are
  invisible to the queue, and lint flags them.

---

## Tier 2 — Evidence

Append-only logs of dated one-line bullets. One format everywhere:

```markdown
# Evidence (append-only)
- YYYY-MM-DD — <one line, ~30 words / 240 chars of claim text — source links and #tags don't count> — Source: [[Meeting or Idea]]
```

- **Pointers, not summaries.** Detail stays in the linked source note. Trust
  weighting (whose voice, what quality) is applied at *decision time*, not capture
  time — the bullet just records who said what, when, where.
- **Permanent.** Evidence is never compacted, drained, or deleted. Growth is cheap;
  the logs are greppable.
- Decided decisions are evidence too: a bullet with a `Decision:` prefix in the
  domain file. Pending ones are captured at distill as `Pending decision:`
  bullets; triage promotes them into Synthesis (its working state) — so each
  tier still has exactly one writer.
- Entity tree inside a tier: `Evidence/<area>/Product.md`, `Org.md`, `Me.md`,
  `Validation.md`, `Partners/<Co>.md`, `People/<Name>.md`, and optionally
  `Topics/<slug>.md` (slug registered in `Metadata/topic_registry.md` first).
- Written only by **distill**, which must lint what it touched before finishing
  (`lint_vault.py --files …`).

---

## Tier 2.5 — Synthesis

One file per area, **rewritten wholesale** at each triage from (previous synthesis +
evidence since). No per-bullet drain bookkeeping, no compaction of evidence — one
`synthesized:` stamp is the entire freshness story.

```markdown
---
area: <area>
synthesized: YYYY-MM-DD
---
# Current synthesis
<capped narrative — what the evidence adds up to, citing [[sources]]>

## People                     # optional: ~3-bullet reads for who matters MOST now
- <Name> — …                  #   full per-person reads live in <area>/people/<Name>.md

## Open decisions             # index — state lives in decisions/<slug>.md
- [[Synthesis/<area>/decisions/<slug>]] — decide-by YYYY-MM-DD

## Open hypotheses
- YYYY-MM-DD — … — Source: [[…]]

## Direction candidates       # the ONLY channel into tier 3
- YYYY-MM-DD — Candidate principle/standard/objective/lens: … — Evidence: [[…]]
```

Size cap: `LEXICON_SYNTHESIS_CAP` lines (default 120) — lint errors above it. The
cap is the discipline: a synthesis that doesn't fit is holding evidence or
operational detail that belongs a tier down.

### Decision-state files

Consequential choices (partner bet, product wedge, hire, direction fork) get a
state file that **persists between sessions** — losing decision state between
meetings is the failure mode this tier exists to prevent.

`Synthesis/<area>/decisions/<slug>.md`:

```markdown
---
area: <area>
opened: YYYY-MM-DD
decide-by: YYYY-MM-DD         # required — undated forks are the failure mode
status: open | committed | killed | held
---
# <Decision>

## Frame
- **Exact decision:** …
- **Success chain:** <falsifiable — step 1 failing vetoes this frame>
- **Forcing event:** …
- **Options:** <include an intersection/test option, not only A vs B>

## Hypotheses                 # what evidence is allowed to change
| ID | Assumption | Confidence | Falsifier | Implication if true |

## Evidence updates           # append-only within the file
| Date | Evidence [[source]] | Quality | Hypothesis | Update type | Action |
<!-- Update types: Veto / Direction / Scope / Execution / Watch -->

## Acceptance test            # FROZEN until a dated Veto/Direction/Scope update
- YYYY-MM-DD — <observable condition, in the buyer's words when external>

## Record                     # on close: decision, why now, what was demoted,
- …                           #   next proof, review trigger, owner, artifact
```

**Monitor rule:** work touching an open decision that contradicts the current
acceptance test, with no new Veto/Direction/Scope update on file, is a
**decision-state conflict** — restore the accepted story or record the evidence
that changed it, before more polish.

`triage_queue.py` surfaces overdue `decide-by` dates and synthesis staleness.

---

## Tier 3 — Constant input

Loaded at the start of **every** session: `Objectives.md` + `Direction/<area>.md`
for the areas in play. Everything here is small, curated, and review-owned —
nothing enters except through a review session reading `## Direction candidates`
(one-liners) or promoting an iterated document from `Sources/Ideas/` (lenses).

### `Direction/<area>.md`

```markdown
---
area: <area>
direction_updated: YYYY-MM-DD
---
# Direction — <Area>

## Purpose
<one paragraph, ≤5 lines — why this area exists>

## Principles                 # standing constraints; cannot be failed
- P1 — <one line> (adopted YYYY-MM-DD — [[source]])

## Standards                  # quality bars; "well-maintained means…"
- S1 — <one line> (adopted YYYY-MM-DD — [[source]])
```

- Exactly these three sections; every item is **one line, ID'd, dated, sourced**.
  IDs are stable — objectives, syntheses, and review logs cite `P2`/`S1` instead of
  paraphrasing.
- Whole-file cap: `LEXICON_DIRECTION_CAP` lines (default 60). Adding an eighth
  principle puts the other seven on screen — the cap is the retirement forcing
  function, same as the objectives cap.
- Operational detail (workflows, file shapes, tooling) belongs in `docs/` and
  rules, never here.

### `Direction/Lenses/<name>.md`

A **lens** is a runnable protocol — a decision process, an evaluation procedure —
too big for a one-line item but normative in use. Review-owned like the rest of
`Direction/`, but **trigger-loaded, not constant-loaded**: a one-line Standard
points at it (`S3 — Consequential decisions run [[Direction/Lenses/<name>]] and
leave a decision record`), and the lens's own `## When to run this` section is the
trigger.

Required shape: `## When to run this`, `## Process`, `## Failure-mode guards`;
cap `LEXICON_LENS_CAP` lines (default 220). Build path: iterate in
`Sources/Ideas/`, promote the final in review, retire the superseded chain.

### `Objectives.md`

Unchanged — see [OBJECTIVES.md](OBJECTIVES.md): max 5 active across all areas,
exactly one `[WIG]`, six required fields. `Evidence:` paths point into the new
tree (`Evidence/<area>/…`, `Synthesis/<area>…`) and **must exist on disk** — a
dead path makes review's evidence step silently empty, so lint errors on it.

---

## The membership test

Where does a durable thing belong?

> No finish line, can't be failed → **Principle** (`Direction/<area>.md`)
> No finish line, but has a quality bar → **Standard** (`Direction/<area>.md`)
> Has a date and can be missed → **Objective** (`Objectives.md`)
> Has a deliverable → it's a **Project** — it does not live in this vault
> Runnable procedure, no finish line, too big for one line → **Lens** (`Direction/Lenses/`), pointed at by a Standard

---

## Who writes what

| Stage | Sources | Evidence | Synthesis | Constant input |
|---|---|---|---|---|
| **Summarize** | creates meeting note | — | — | — |
| **Distill** | `# Distilled` stamp only | **append**, then lint | — | — |
| **Triage** | read-only; Ideas queue (promote/retire) | read-only | **rewrite** `<area>.md`; update decision files; stage candidates | read-only |
| **Review** | read-only | read-only | reads `## Direction candidates` | **only writer** |
| **Query** | read-only | read-only | read-only | read-only |

---

## QA system

| Layer | Checks | Enforced by |
|---|---|---|
| **Schema** | Per-directory contracts: Evidence bullets dated/one-line/no orphaned sub-bullets or undated blocks; Synthesis stamp + cap + sections; Direction three-sections + item shape + cap; Lens shape + cap; decision files have `decide-by` + dated acceptance test; Sources frontmatter | `scripts/lint_vault.py` — full run, or `--files` in the write-time gate every writer runs before finishing |
| **Provenance** | Every Direction item dated + sourced; every objective's `Evidence:` paths exist | `lint_vault.py` |
| **Process** | Tier 3 diffs without a same-week `Metadata/review/` log; Synthesis diffs without a recap log | `lint_vault.py` (warning) |
| **Usage** | Are constant inputs actually read? Which evidence is never consulted? Is a lens ever fired? | usage hook → `Metadata/usage/access.jsonl` → `scripts/usage_report.py`, surfaced by the queue scripts |

The caps and schemas are hypotheses; the usage layer is how they get revised with
data instead of opinion.

---

## Principles

1. **The path is the contract** — tier, mutability, and owner are functions of the top-level directory.
2. **Recall at capture, precision at query** — generous summarize; evidence bullets are pointers.
3. **Evidence is sacred and permanent** — never rewritten, never compacted; trust is weighed at decision time.
4. **Synthesis is rewritten, not drained** — one stamp per area, no bookkeeping that can half-complete.
5. **Nothing enters constant input except through review** — via `## Direction candidates` or a promoted document, always with provenance.
6. **No obligation without a mechanism** — anything "someone should remember to do" is a script, a lint check, or it doesn't exist.
7. **Decision state outlives the meeting** — consequential choices get a state file with a frozen acceptance test and a `decide-by`.
8. **Retire = delete** — git preserves history; Ideas are promoted or deleted, never archived in place.
9. **Route by subject, not source** — evidence goes to the area it is *about*.
10. **Measure the experiment** — file reads are logged by hook; structure earns its keep in the usage report.

See also: `.cursor/rules/`, `.cursor/skills/`, [OBJECTIVES.md](OBJECTIVES.md), [SETUP.md](SETUP.md), [UPDATING.md](UPDATING.md).
