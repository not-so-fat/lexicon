---
area: Lexicon
direction_updated: 2026-07-26
---

# Direction — Lexicon

*Normative tier: the charter for the Lexicon pipeline itself. What is **true** about
this area → `Memory/Lexicon/`. Horizon-bound intentions → `Objectives.md`.*

Generic — use this in any vault clone; no project-specific content here.

---

## Purpose

**Turn conversations and thinking into queryable organizational memory — current truth on top, traceable evidence underneath.**

| Today (without triage) | With triage |
|---|---|
| Accumulate facts | Maintain **current truth** + evidence |
| Append-only Memory | Evidence append-only; **synthesis revisable** |
| Rich capture everywhere | Rich **capture**; disciplined **Memory** |
| Folders grow forever | **Triage** retires or routes what doesn't belong |

---

## Principles

### Two loops

The knowledge loop keeps track of what is true. The intent loop keeps track of
what you are trying to make true. They share evidence and nothing else.

| Loop | Stages | Scope | Cadence |
|---|---|---|---|
| **Knowledge** | Ingest → Summarize → Distill → Triage → Query | per area | as material arrives |
| **Intent** | Review | global, all areas | weekly |

**Hard boundaries:**

- Distill never edits `# Current model`.
- Triage never edits meeting notes and never appends meeting evidence, and never writes `Objectives.md` or `Direction/**`.
- Review never writes `Memory/`, `People/` or meeting notes.

There is **no separate reconcile stage**. Synthesis happens only in **triage** (with
your approval), informed by distill evidence.

### Who owns each stage

| Stage | Who | Purpose |
|---|---|---|
| **Ingest** | Script | Fetch transcripts. Immutable. |
| **Summarize** | Agent | Transcript → meeting note. Generous capture. |
| **Distill** | Agent | Meeting → **evidence** in People / Memory. **No synthesis.** |
| **Triage** | Agent + you | **Interactive.** Recap, update **current truth**, clean **Ideas** queue, recap log. Meetings read-only. |
| **Query** | Agent | Natural language over the vault. |
| **Review** | Agent + you | **Interactive.** Re-anchor on objectives, read their evidence, propose status, retire. Memory read-only. |

### Knowledge tiers

| Tier | What | Mutability |
|---|---|---|
| **Evidence** | Meetings, transcripts, `# Evidence Log`, `<Area>.evidence.md` logs | Append-only |
| **Working** | `# Current read` / `# Current model` on Memory area files | Updated in **triage** |
| **Direction** | `Direction/<area>.md` — purpose, principles, standards | Updated in **review** (rare; human approval) |
| **Intent** | `Objectives.md` — horizon-bound, capped, one WIG | Updated in **review** (weekly) |

Agents read **top-down** for truth questions: Direction → current model → evidence.
Area layout keeps working truth and evidence in separate files so the top-down read
stays cheap. For intent questions, read `Objectives.md` first — see
`docs/OBJECTIVES.md`.

### Triage is an interactive memory session

**Not a meeting inbox.** Triage is a conversation about how things are going, what's
open, and what Memory should say now — plus cleaning the **Ideas** queue.

Meetings are handled by **Summarize → Distill** (evidence only). Triage **reads**
recent meetings for recap; it does **not** edit them.

The user kicks triage; confirm the **period** if unclear (suggest since last triage
or ~2 weeks; never all-time by default).

> **"Triage `<project>` — last two weeks."**

```bash
python3 scripts/triage_queue.py --project <project> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
```

The script returns: **previous triage**, **pending decisions**, **evidence debt**
(area layout), **recent meetings (context)**, **ideas queue**.

Session flow, in order:

1. **Recap together** — what happened, how you're doing, open problems.
2. **Discuss** — direction shifts, resolve or carry forward open decisions.
3. **Update Memory** — `# Current model` / durable sections, `# Current read` (you approve writes). **Drain evidence debt:** fold un-drained bullets into `# Current model` and stamp `model_updated:` — or explicitly defer. A **⚠ STALE** flag (model lagging newest evidence > 21 days) must not survive the session unaddressed.
4. **Clean Ideas** — Promote → memory, Retire stale drafts, Keep / Skip exploring notes.
5. **Recap log** — append `Metadata/recap/<project>/YYYY-MM.md`.

Principle-level commits are **not** triage's to make: they belong to review.

### Ideas dispositions

| Disposition | Meaning |
|---|---|
| **Promote** | Synthesis → Memory; idea: `triaged`, `status: promoted`, `promotes-to` |
| **Keep** | You will **keep editing** the file in `Ideas/` — not promoted yet |
| **Skip** | Not now — **no `triaged`** (stays in queue) |
| **Retire** | Delete idea file (git preserves history) |
| **Move** | Relocate; set `triaged` when done |

**User rule:** **Keep** only if you will keep editing the idea file. Otherwise
**Promote** or **Retire**.

### Standing rules

1. AI-first retrieval — structure for agents, not reading pleasure.
2. Evidence is sacred — transcripts and meeting notes aren't rewritten.
3. Synthesis is revisable — updated in **triage** with user approval.
4. Recall at capture, precision at query — generous summarize; **triage** for Memory.
5. Provenance always — date, source, confidence when interpretive.
6. **One triage process** — recap, queue, promote — one habit per area.
7. Capture decays by default — **Retire = delete**; promote keeps capture with `status: promoted`.
8. Human gate on **Direction** and **Objectives** — normative edits need explicit approval, in **review**.
9. **No numeric alignment score.** Review proposes `moving` / `stalled` / `drifting`; the verdict is the user's.

---

## Standards

What a well-maintained vault looks like. No finish line — a bar to hold.

### Memory layouts (pick one per area)

**Area files** — recommended for mature areas:

```
Memory/<project>/
  Validation.md              # market learnings + ## Open hypotheses
  Validation.evidence.md     # append-only evidence log (distill)
  Org.md                     # + ## Open decisions
  Org.evidence.md
  Product.md                 # + ## Open decisions
  Product.evidence.md
  Me.md
  Me.evidence.md
  Partners/<Company>.md      # + ## Open decisions
  Partners/<Company>.evidence.md

People/<project>/<Person>.md   # # Current read (triage) + # Evidence Log (distill)
```

**Topic slugs** — default for new / small areas:

```
Memory/<project>/
  Product/<topic>.md    # # What we learned + # Evidence
  Org/<topic>.md
  Decisions/decisions.md
  Personal/self_evaluation.md

People/<project>/<Person>.md
```

Detect layout: if `Memory/<project>/Product.md` exists, use area files; else use
topic slugs. Triage on topic-slug areas refreshes durable sections
(`# What we learned`, `# Signals`) and the decisions log — not `# Current model`
unless you adopt area files.

`Memory/<project>/` holds no `Direction.md`: the normative tier lives at
`Direction/<area>.md`, one level up and outside `Memory/`.

### File shape

Each area **model file** holds synthesis only:

```markdown
---
model_updated: YYYY-MM-DD    # stamped by triage on every # Current model refresh
---

# Current model
<what a stranger needs now>
```

…followed by an `## Open decisions` section — a dated pending list, one line each:
`- YYYY-MM-DD — Pending: … — Source: [[…]]`.

The sibling **evidence file** (`<Area>.evidence.md`) is an append-only log:

```markdown
# Evidence (append-only)
- YYYY-MM-DD — <one line, ~30 words max> — Source: [[Meeting or Idea]]
```

Evidence bullets are **one line** and greppable pointers, not re-summaries — detail
stays in the linked meeting note. Legacy inline `# Evidence` sections in model files
are read-only: new bullets go to the sibling file, and triage migrates the old
section over.

Capture files (Ideas / Clippings) carry only `project` + `created` at capture;
triage completes the rest:

```yaml
---
project: <project>
created: YYYY-MM-DD
tags: [idea]
status:                    # set at triage
triaged:                   # empty = in queue
triage_note:
promotes-to:               # when status: promoted
---
```

Templates: `.cursor/templates/ideas_template.md`, `.cursor/templates/clipping_template.md`.

### The bar

- **Registries stay trustworthy** — `Metadata/*_registry.md` is the index; new topics and tags are registered before use.
- **No hand-maintained maps** — folder structure and registries are the index. Never hand-write `Index.md`-style files.
- **Evidence debt gets drained** — no area carries a `# Current model` that lags its newest evidence by more than 21 days without an explicit deferral.
- **Objectives stay under the cap** — no more active objectives across all areas than the cap allows (5 by default; `LEXICON_OBJECTIVE_CAP` overrides), exactly one `[WIG]`, retire before opening one more.
- **The vault lints clean** — `python3 scripts/lint_vault.py` exits 0.

### Who writes what

| Stage | Memory impact | Meetings | Ideas | Normative tier |
|---|---|---|---|---|
| **Summarize** | Creates meeting note | Created/updated | — | — |
| **Distill** | Append evidence only (**`<Area>.evidence.md`** on area layout); factual **Open decisions** from meeting | `# Distilled` updated; **no `triaged`** | — | — |
| **Triage** | Refresh **`# Current model`** + stamp `model_updated:` (or durable sections); drain evidence debt; resolve open decisions; People **`# Current read`** | **Read-only** for recap | Promote / Retire / Keep queue | **Read-only** |
| **Review** | **Read-only** | **Read-only** | — | `Objectives.md`, `Objectives.evidence.md`, `Direction/<area>.md` |

### Tooling

| What | Path |
|---|---|
| Triage queue script | `scripts/triage_queue.py` |
| Review queue script | `scripts/review_queue.py` |
| Lint | `scripts/lint_vault.py` |
| Agent skills | `.cursor/skills/lexicon-triage/SKILL.md`, `.cursor/skills/lexicon-review/SKILL.md` |
| Rules | `.cursor/rules/triage.mdc`, `.cursor/rules/review.mdc` |
| Recap logs | `Metadata/recap/<project>/YYYY-MM.md` |
| Review logs | `Metadata/review/YYYY-Www.md` |
