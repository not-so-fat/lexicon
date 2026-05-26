# Lexicon Processing Strategy

Generic charter for the Lexicon pipeline. Use this in any vault clone — no project-specific content here.

---

## Goal

**Turn conversations and thinking into queryable organizational memory — current truth on top, traceable evidence underneath.**

| Today (without triage) | With triage |
|---|---|
| Accumulate facts | Maintain **current truth** + evidence |
| Append-only Memory | Evidence append-only; **synthesis revisable** |
| Rich capture everywhere | Rich **capture**; disciplined **Memory** |
| Folders grow forever | **Triage** retires or routes what doesn't belong |

---

## Pipeline (five stages)

```
Ingest → Summarize → Distill → Triage → Query
         (meetings)   (evidence) (synthesis + ideas)
```

| Stage | Who | Purpose |
|---|---|---|
| **Ingest** | Script | Fetch transcripts. Immutable. |
| **Summarize** | Agent | Transcript → meeting note. Generous capture. |
| **Distill** | Agent | Meeting → **evidence** in People / Memory. **No synthesis.** |
| **Triage** | Agent + you | **Interactive.** Recap, update **current truth**, clean **Ideas** queue, recap log. Meetings read-only. |
| **Query** | Agent | Natural language over the vault. |

There is **no separate reconcile stage**. Synthesis happens only in **triage** (with your approval), informed by distill evidence.

**Hard boundary:** Distill never edits `# Current model`. Triage never edits meeting notes or appends meeting evidence.

---

## Knowledge tiers

| Tier | What | Mutability |
|---|---|---|
| **Evidence** | Meetings, transcripts, `# Evidence Log`, append sections | Append-only |
| **Working** | `# Current read` / `# Current model` on Memory area files | Updated in **triage** |
| **Direction** | Principles only (`Direction.md`) | Updated in **triage** (rare; human approval) |

Agents read **top-down**: Direction → current model → evidence.

---

## Memory layouts (pick one per project)

### Area files (recommended for mature projects)

```
Memory/<project>/
  Direction.md          # principles only
  Validation.md         # market learnings + ## Open hypotheses
  Org.md                # + ## Open decisions
  Product.md            # + ## Open decisions
  Me.md
  Partners/<Company>.md # + ## Open decisions

People/<project>/<Person>.md   # # Current read (triage) + # Evidence Log (distill)
```

Each area file:

```markdown
# Current model (last updated: YYYY-MM-DD)
<what a stranger needs now>

## Open decisions
- YYYY-MM-DD — Pending: … — Source: [[…]]

# Evidence (append-only)
- YYYY-MM-DD — … — Source: [[Meeting or Idea]]
```

### Topic slugs (default for new / small projects)

```
Memory/<project>/
  Product/<topic>.md    # # What we learned + # Evidence
  Org/<topic>.md
  Decisions/decisions.md
  Personal/self_evaluation.md

People/<project>/<Person>.md
```

Triage on topic-slug projects refreshes durable sections (`# What we learned`, `# Signals`) and the decisions log — not `# Current model` unless you adopt area files.

Detect layout: if `Memory/<project>/Product.md` exists, use area files; else use topic slugs.

---

## Triage — interactive memory session

**Not a meeting inbox.** Triage is a conversation about how things are going, what's open, and what Memory should say now — plus cleaning the **Ideas** queue.

Meetings are handled by **Summarize → Distill** (evidence only). Triage **reads** recent meetings for recap; it does **not** edit them.

### How you run it

User kicks triage — confirm **period** if unclear (suggest since last triage or ~2 weeks; never all-time by default).

> **"Triage `<project>` — last two weeks."**

```bash
python3 scripts/triage_queue.py --project <project> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
```

Script returns: **previous triage**, **pending decisions**, **recent meetings (context)**, **ideas queue**.

### Session flow

1. **Recap together** — what happened, how you're doing, open problems.
2. **Discuss** — direction shifts, resolve or carry forward open decisions.
3. **Update Memory** — `# Current model` / durable sections, `# Current read`, rare Direction (you approve writes).
4. **Clean Ideas** — Promote → memory, Retire stale drafts, Keep / Skip exploring notes.
5. **Recap log** — append `Metadata/recap/<project>/YYYY-MM.md`.

### Ideas dispositions

| Disposition | Meaning |
|---|---|
| **Promote** | Synthesis → Memory; idea: `triaged`, `status: promoted`, `promotes-to` |
| **Keep** | You will **keep editing** the file in `Ideas/` — not promoted yet |
| **Skip** | Not now — **no `triaged`** (stays in queue) |
| **Retire** | Delete idea file (git preserves history) |
| **Move** | Relocate; set `triaged` when done |

**User rule:** **Keep** only if you will keep editing the idea file. Otherwise **Promote** or **Retire**.

### Capture frontmatter (Ideas / Clippings)

At capture — only `project` + `created`. Triage completes the rest:

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

### Tooling

| What | Path |
|---|---|
| Queue script | `scripts/triage_queue.py` |
| Agent skill | `.cursor/skills/lexicon-triage/SKILL.md` |
| Rule | `.cursor/rules/triage.mdc` |
| Recap logs | `Metadata/recap/<project>/YYYY-MM.md` |

---

## Distill vs triage

| Stage | Memory impact | Meetings | Ideas |
|---|---|---|---|
| **Summarize** | Creates meeting note | Created/updated | — |
| **Distill** | Append **`# Evidence`** only; factual **Open decisions** from meeting | `# Distilled` updated; **no `triaged`** | — |
| **Triage** | Refresh **`# Current model`** (or durable sections); resolve open decisions; People **`# Current read`** | **Read-only** for recap | Promote / Retire / Keep queue |

---

## Principles

1. AI-first retrieval — structure for agents, not reading pleasure.
2. Evidence is sacred — transcripts and meeting notes aren't rewritten.
3. Synthesis is revisable — updated in **triage** with user approval.
4. Recall at capture, precision at query — generous summarize; **triage** for Memory.
5. Provenance always — date, source, confidence when interpretive.
6. **One triage process** — recap, queue, promote, canon — one habit per project.
7. Capture decays by default — **Retire = delete**; promote keeps capture with `status: promoted`.
8. Human gate on **Direction** — principle edits need explicit approval in triage.
