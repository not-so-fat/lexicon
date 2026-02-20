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
2. **Read registries** — Read `Metadata/project_registry.md`, `Metadata/topic_registry.md`, and `Metadata/tag_registry.md`. These are needed for Step 3.
3. **Create meeting note** — Path: `Meetings/<Project>/YYYY-MM-DD [Title].md`. Apply `.cursor/rules/summarize.mdc` (all steps). Key points from registries:
   - **Project**: transcript's `project` is the default. Override if content clearly belongs to a different project in the registry.
   - **Topics**: use canonical slugs from the topic registry. Add new topics to the registry before using them.
   - **Tags**: use only property tags from the tag registry (max 3). No subject-like tags.
4. **Link** — Include a Transcript Link section pointing to the source file.
5. **Reply** — Tell user the note path. For manual transcripts, suggest reviewing speaker attribution before distilling.

## Error handling

- **No transcript file** — Don't create one here. Tell user to use the manual-template skill.
- **Missing project** — Ask user which project (check `Metadata/project_registry.md` for valid options).
