---
name: lexicon-summarize
description: Create a meeting note from an existing transcript file. Use when user says "summarize this transcript", "create a meeting note", or points at a file under Transcripts/.
---

# Summarize transcript into meeting note

Turns one transcript file into a structured meeting note under `Meetings/<Project>/`.

## Prerequisites

An existing transcript file under `Transcripts/Fireflies/<account>/` or `Transcripts/Manual/`. If the user has no file yet, direct them to the **lexicon-manual-template** skill first.

## Steps

1. **Read transcript** — Identify the file. Read its frontmatter (`project`, `title`, `date`, `participants` or `with_whom`).
2. **Determine project** — Use `project` from frontmatter only. If missing, ask the user.
3. **Create meeting note** — Path: `Meetings/<Project>/YYYY-MM-DD [Title].md`. Apply `.cursor/rules/summarize.mdc` (all steps and sections defined there).
4. **Link** — Include a Transcript Link section pointing to the source file.
5. **Reply** — Tell user the note path. For manual transcripts, suggest reviewing speaker attribution before distilling.

## Error handling

- **No transcript file** — Don't create one here. Tell user to use the manual-template skill.
- **Missing project** — Ask user which project (personal, company, career, general).
