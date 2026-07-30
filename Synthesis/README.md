# Synthesis

**Tier 2.5 — what the evidence adds up to.** Owned by triage; rewritten, not drained.

```
Synthesis/
  <area>.md                   # one per area — rewritten wholesale each triage
  <area>/decisions/<slug>.md  # per-decision state files
  <area>/people/<Name>.md     # per-person current reads (sibling facts: Evidence/<area>/People/)
  <area>/partners/<Co>.md     # per-partner current reads (facts: Evidence/<area>/Partners/)
```

`<area>.md` carries a `synthesized:` frontmatter stamp (the entire freshness
story), a capped narrative citing sources, optional `## People` current reads,
an `## Open decisions` index, `## Open hypotheses`, and `## Direction candidates`
— the **only** channel through which anything reaches `Direction/` or
`Objectives.md` (review reads it and promotes or rejects).

Decision-state files persist consequential choices between sessions: frame,
hypotheses with falsifiers, typed evidence updates (Veto / Direction / Scope /
Execution / Watch), a **frozen acceptance test**, and a required `decide-by`
date. Work that contradicts the acceptance test with no new typed update on file
is a **decision-state conflict** — restore the story or record the evidence.

**Contract:** written only in triage (or a decision session) with your approval;
size caps enforced by `lint_vault.py`; evidence is never deleted to keep this
tier small — the cap forces selectivity, not compaction.

See [docs/MEMORY_MODEL.md](../docs/MEMORY_MODEL.md) for full schemas.
