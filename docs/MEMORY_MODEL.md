# Lexicon Memory Model

How Lexicon organizes durable knowledge after meetings are summarized and distilled.

**Pipeline:** Ingest → Summarize → **Distill** (facts) → **Triage** (synthesis) → Query

---

## Three tiers of truth

| Tier | What | Mutability |
|------|------|------------|
| **Evidence** | Meeting notes, transcripts, `# Evidence` append sections | Append-only |
| **Working** | `# Current model`, `# Current read`, `## Open decisions` | Updated in **triage** |
| **Direction** | Principles only (`Direction.md`) | Rare; human approval in triage |

Agents read **top-down**: Direction → current model → evidence.

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
  Direction.md            # principles only
  Validation.md           # market learnings (optional but recommended)
  Product.md              # + ## Open decisions
  Org.md
  Me.md
  Partners/<Company>.md   # + ## Open decisions
  _legacy/                # archives, topic dumps, old logs
```

**Distill:** append `# Evidence` only — **never** `# Current model`. Run after meetings, not in triage.  
**Triage Promote:** refresh `# Current model`, resolve open decisions.  
**Triage Canon:** edit `Direction.md` for principle-level commits.

---

## Validation (optional area file)

Use when cross-partner market patterns need a reviewable home separate from product build decisions.

Suggested sections:

- **Validated / Working / Refuted** — cross-cutting market learnings
- **By segment** — developers, enterprise, merchants, etc.
- **Open hypotheses** — still testing (surfaced in every triage recap)
- **Evidence** — append-only dated bullets with meeting sources

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

See also: `.cursor/rules/triage.mdc`, `.cursor/rules/distill.mdc`, `.cursor/skills/lexicon-triage/`.


## Meetings vs Ideas

| | Meetings | Ideas |
|---|---|---|
| **Pipeline** | Summarize → Distill | Triage queue |
| **Memory writes** | `# Evidence` only (distill) | Promote → `# Current model` (triage) |
| **`triaged` frontmatter** | Never | On Ideas/Clippings when processed |

Triage **reads** recent meetings for recap; it does not edit them.
