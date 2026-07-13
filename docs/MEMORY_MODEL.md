# Lexicon Memory Model

How Lexicon organizes durable knowledge after meetings are summarized and distilled.

**Pipeline:** Ingest → Summarize → **Distill** (facts) → **Triage** (synthesis) → Query

---

## Three tiers of truth

| Tier | What | Mutability |
|------|------|------------|
| **Evidence** | Meeting notes, transcripts, `<Area>.evidence.md` logs | Append-only |
| **Working** | `# Current model`, `# Current read`, `## Open decisions` | Updated in **triage** |
| **Direction** | Principles only (`Direction.md`) | Rare; human approval in triage |

Agents read **top-down**: Direction → current model → evidence. In the area layout, working truth and evidence live in **separate files**, so loading the current model never pays for the evidence log.

---

## Two memory layouts (both supported)

### Classic layout (default for new projects)

Best for personal vaults and early-stage projects.

```
Memory/<project>/
  Product/<topic>.md      # e.g. pricing, session, partnership
  Org/<topic>.md          # e.g. hiring, execution
  Decisions/decisions.md  # pending + decided log
  Personal/ai_evaluation.md
```

Distill appends to topic files and logs. Triage can later migrate to area files.

### Area files layout (mature projects)

Best when topic slugs overlap or synthesis needs a single current truth per domain.

```
Memory/<project>/
  Direction.md               # principles only
  Validation.md              # market learnings (optional but recommended)
  Validation.evidence.md     # append-only evidence log
  Product.md                 # + ## Open decisions
  Product.evidence.md
  Org.md
  Org.evidence.md
  Me.md
  Me.evidence.md
  Partners/<Company>.md      # + ## Open decisions
  Partners/<Company>.evidence.md
  _legacy/                   # archives, topic dumps, old logs
```

**Model files** (`Product.md`, `Org.md`, …) hold synthesis only: frontmatter `model_updated: YYYY-MM-DD`, `# Current model`, and `## Open decisions` / `## Open hypotheses`. Keep them small — this is the layer agents load first, and the loadable working-truth layer for cross-project Q&A.

**Evidence files** (`Product.evidence.md`, …) are append-only logs of dated one-line bullets:

```markdown
# Evidence (append-only)
- YYYY-MM-DD — <one line, ~30 words max> — Source: [[Meeting or Idea]]
```

Detail stays in the linked meeting note — evidence bullets are pointers, not summaries.

**Distill:** append to `<Area>.evidence.md` only (create it if missing) — **never** `# Current model`. Run after meetings, not in triage.  
**Triage Promote:** drain un-drained evidence into `# Current model`, stamp `model_updated:`, resolve open decisions.  
**Triage Canon:** edit `Direction.md` for principle-level commits.

**Legacy inline evidence:** older vaults kept `# Evidence` inside the model file. Treat that section as read-only legacy: new bullets go to the sibling `.evidence.md`, and the old section is moved over during a triage session. `triage_queue.py` counts both and flags un-migrated sections.

---

## Validation (optional area file)

Use when cross-partner market patterns need a reviewable home separate from product build decisions.

Suggested sections:

- **Validated / Working / Refuted** — cross-cutting market learnings
- **By segment** — developers, enterprise, merchants, etc.
- **Open hypotheses** — still testing (surfaced in every triage recap)

Evidence lives in the sibling `Validation.evidence.md` — append-only dated bullets with meeting sources.

---

## People pages

```
People/<project>/<Name>.md
  # Current read        (~5 bullets — refreshed in triage)
  # Evidence Log        (append-only)
```

---

## Triage routing

| Signal | Promote to |
|--------|------------|
| Cross-partner market pattern | **Validation** `# Current model` |
| Still testing | **Validation** `## Open hypotheses` |
| Product consequence | **Product** `# Current model` |
| Committed principle | **Direction** (human approval) |
| Partner deal | **Partners/<Co>.md` |
| Org/process | **Org** |
| Your performance pattern | **Me** |

---

## Queue and recap

**Untriaged** = **Ideas/Clippings** with no `triaged:` date. Meetings are never in the queue.

```bash
python3 scripts/triage_queue.py --project <project> [--since YYYY-MM-DD]
```

On area-file projects the queue also reports **evidence debt** per area: bullets newer than `model_updated:`, a **⚠ STALE** flag when the current model lags the newest evidence by more than 21 days, plus un-migrated inline `# Evidence` sections and `_legacy/` content. Every triage session reviews this section — drain the debt into `# Current model` or explicitly defer it.

Frontmatter and evidence hygiene is checked by:

```bash
python3 scripts/lint_vault.py
```

Each triage session appends to:

```
Metadata/recap/<project>/YYYY-MM.md
```

---

## Principles

1. **Recall at capture, precision at query** — generous summarize; triage for Memory.
2. **Evidence is sacred** — don't rewrite meeting notes or transcripts.
3. **Synthesis is revisable** — dated `# Current model`, not chronological dumps.
4. **One triage habit** — Ideas/Clippings queue; meetings via distill only.
5. **Skip stays in queue** — only set `triaged` when processed or explicitly Keep'd.
6. **Retire = delete** — git preserves history; promote keeps capture with `status: promoted`.
7. **Route by subject, not source** — evidence goes to the Memory project it is *about*; the capture account/venue is only a default hint.
8. **No hand-maintained maps** — registries and folder structure are the index; `lint_vault.py` keeps them trustworthy. Never hand-write `Index.md`-style files.

See also: `.cursor/rules/triage.mdc`, `.cursor/rules/distill.mdc`, `.cursor/skills/lexicon-triage/`.


## Meetings vs Ideas

| | Meetings | Ideas |
|---|---|---|
| **Pipeline** | Summarize → Distill | Triage queue |
| **Memory writes** | Evidence only (distill; `<Area>.evidence.md` on area layout) | Promote → `# Current model` (triage) |
| **`triaged` frontmatter** | Never | On Ideas/Clippings when processed |

Triage **reads** recent meetings for recap; it does not edit them.
