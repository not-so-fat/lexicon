---
area: Lexicon
direction_updated: 2026-07-29
---

# Direction — Lexicon

## Purpose

Turn conversations and thinking into queryable organizational memory — constant
direction on top, revisable synthesis in the middle, traceable evidence
underneath, raw sources at the bottom. Structured for agent retrieval, not
reading pleasure.

## Principles

- P1 — The path is the contract: tier, mutability, and owner are functions of the top-level directory. (adopted 2026-07-29 — [[docs/MEMORY_MODEL]])
- P2 — Evidence is sacred and permanent: never rewritten, never compacted; trust is weighed at decision time, not capture time. (adopted 2026-07-29)
- P3 — Synthesis is rewritten, not drained: one stamp per area; no bookkeeping that can half-complete. (adopted 2026-07-29)
- P4 — Nothing enters constant input except through review, always with provenance. (adopted 2026-07-29)
- P5 — No obligation without a mechanism: anything "someone should remember to do" is a script, a lint check, or it doesn't exist. (adopted 2026-07-29)
- P6 — Recall at capture, precision at query: generous summarize; evidence bullets are pointers, not summaries. (adopted 2026-07-26)
- P7 — Route by subject, not source: evidence goes to the area it is about, wherever it was captured. (adopted 2026-07-26)
- P8 — Human gate on synthesis and direction: triage and review propose, you approve; no numeric alignment score. (adopted 2026-07-26)
- P9 — Decision state outlives the meeting: consequential choices get a state file with a frozen acceptance test. (adopted 2026-07-29)

## Standards

- S1 — The vault lints clean: `lint_vault.py` exits 0, and every writer lints the files it touched before finishing. (adopted 2026-07-29)
- S2 — No stale synthesis: an area with evidence newer than its `synthesized:` stamp by >21 days is flagged and addressed at the next triage. (adopted 2026-07-29)
- S3 — Every open decision carries a `decide-by` date and a dated acceptance test; overdue dates surface in the triage queue. (adopted 2026-07-29)
- S4 — Objectives stay under the cap (5 across all areas), exactly one WIG; retire before opening. (adopted 2026-07-26)
- S5 — Registries stay trustworthy: topics and tags are registered before use; no hand-maintained maps. (adopted 2026-07-26)
- S6 — Capture decays by default: Ideas and Clippings are promoted or deleted at triage, never archived in place. (adopted 2026-07-26)
- S7 — Structure earns its keep: file reads are logged, and the usage report informs what gets kept, promoted, or retired. (adopted 2026-07-29)
