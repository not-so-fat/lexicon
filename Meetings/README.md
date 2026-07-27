# Meetings

Summarized meeting notes, one file per meeting: `Meetings/<area>/YYYY-MM-DD Title.md`.

**Written by:** the summarize step (`lexicon-summarize` skill), from a raw transcript in `Transcripts/`.

**Read by:** distill (to extract evidence), triage recap (read-only context — triage never edits a meeting note), and anyone querying "what happened in that meeting with X."

**What does NOT belong here:**
- Your own thoughts, brainstorms, or research → `Ideas/<area>/`
- Durable facts and decisions → `Memory/<area>/` (via distill)
- Horizon-bound intentions → `Objectives.md`
- Standing principles → `Direction/<area>.md`

Meetings are never triaged and never carry a `triaged:` frontmatter field — that field belongs to `Ideas/` and `Clippings/` only. See [docs/MEMORY_MODEL.md](../docs/MEMORY_MODEL.md).
