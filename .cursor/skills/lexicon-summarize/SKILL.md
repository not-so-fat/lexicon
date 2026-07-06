---
name: lexicon-summarize
description: Create a meeting note from an existing transcript file. Use when user says "summarize this transcript", "create a meeting note", or points at a file under Transcripts/.
---

# Summarize transcript into meeting note

Turns one transcript file into a structured meeting note under `Meetings/<Project>/`.

## Prerequisites

An existing transcript file under `Transcripts/Fireflies/<account>/`, `Transcripts/HiDock/`, or `Transcripts/Manual/`. If the user has no file yet, direct them to the **lexicon-manual-template** skill first.

## Steps

1. **Read transcript** — Identify the file. Read frontmatter (`title`, `date`, `signature` for HiDock; `project`, `participants` or `with_whom` when present).
2. **Read registries** — Read `Metadata/project_registry.md`, `Metadata/topic_registry.md`, and `Metadata/tag_registry.md`. These are needed for Step 3. If a registry file is missing, fall back to best-effort choices and note that the registry is absent.
3. **Create meeting note** — Path: `Meetings/<Project>/YYYY-MM-DD [Title].md`. Apply `.cursor/rules/summarize.mdc` (all steps). Key points from registries:
   - **Project**: Fireflies/Manual — transcript's `project` is the default. HiDock — no `project` in transcript; infer from content + registry. Override if clearly mismatched.
   - **HiDock**: set `source: HiDock`, `hidock_signature: <signature>` on the meeting note; link `Transcripts/HiDock/...`.
   - **HiDock speakers**: infer `Speaker N` → person from dialogue; then **write back** to the transcript file (`participants:` frontmatter + replace `Speaker N:` lines with `Full Name:`). If uncertain, leave `Speaker N:` and note in meeting Context only.
   - **Topics**: use canonical slugs from the topic registry. Add new topics to the registry before using them.
   - **Tags**: use only property tags from the tag registry (max 3). No subject-like tags.
4. **Link** — Include a Transcript Link section pointing to the source file.
5. **Reply** — Tell user the note path. For HiDock, confirm speaker labels were written back (or flag what still needs review). For manual transcripts, suggest reviewing speaker attribution before distilling.

## Error handling

- **No transcript file** — Don't create one here. Tell user to use the manual-template skill.
- **Missing project** — Ask user which project (check `Metadata/project_registry.md`). Required for HiDock and any transcript without `project` in frontmatter.
