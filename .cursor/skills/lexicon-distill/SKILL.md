---
name: lexicon-distill
description: Extract durable knowledge from a meeting note into People, Memory, and Metadata. Use when user says "distill this meeting note", "distill this note", or "extract knowledge from this meeting".
---

# Distill meeting note into memory

Updates `People/<Project>/`, `Memory/<Project>/`, and `Metadata/` from one meeting note. Fills the note's **# Distilled** section.

## Prerequisites

A meeting note under `Meetings/<Project>/`. The note is the source of truth (user may have edited it after summarize).

## Steps

1. **Read the meeting note** — Identify the file under `Meetings/<Project>/`.
2. **Read registries** — Read `Metadata/topic_registry.md` (for topic matching) and list existing files under `Memory/<Project>/Product/` and `Memory/<Project>/Org/` (for match-before-create).
3. **Apply distill rule** — Follow `.cursor/rules/distill.mdc` in full. Key additions:
   - **Topic matching**: before creating a new Memory topic file, check the topic registry for canonical slugs and aliases. Use existing topics when possible. Add genuinely new topics to the registry.
   - **Inline `#topic`**: when writing a bullet to a Memory or People page, append `#topic_slug` if the fact also relates to another registered topic.
   - **Relationships**: when signals reveal interpersonal dynamics, update the `# Relationships` section on **both** people's pages.
4. **Fill # Distilled** — In the meeting note, list every file you updated.
5. **Reply** — Confirm done and list updated files.

## Error handling

- **No meeting note** — Ask user which note to distill.
- **Note has no project** — Ask user which project (check `Metadata/project_registry.md`).
- **Append-only** — Never overwrite past entries in People or Memory; always append.
