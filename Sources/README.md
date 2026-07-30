# Sources

**Tier 1 — write-once captures.** Everything the pipeline starts from.

| Subdir | What | Enters via |
|---|---|---|
| `Meetings/<area>/` | Summarized meeting notes | summarize |
| `Transcripts/` | Raw transcripts | ingest scripts |
| `Ideas/<area>/` | Your thinking captures | you |
| `Clippings/` | Web clips, external material | you |

**Contract:** files here are never edited after capture, with two exceptions —
meeting notes take a `# Distilled` traceability stamp, and Ideas/Clippings are
editable **until triaged**, then promoted or deleted (git preserves history).
Nothing lives in `Ideas/` permanently.

Every file carries frontmatter (`area:`, `created:`) — without it the file is
invisible to the queue, and `lint_vault.py` flags it.

**What does NOT belong here:** durable facts (→ `Evidence/`, via distill),
synthesis (→ `Synthesis/`, via triage), principles or objectives (→ `Direction/`,
`Objectives.md`, via review). See [docs/MEMORY_MODEL.md](../docs/MEMORY_MODEL.md).
