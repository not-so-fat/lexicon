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
2. **Apply distill rule** — Follow `.cursor/rules/distill.mdc` in full (routing, People pages, Memory pages, Decisions, Personal, traceability).
3. **Fill # Distilled** — In the meeting note, list every file you updated (e.g. `[[People/personal/Alice]]`, `[[Memory/personal/Product/pricing]]`).
4. **Reply** — Confirm done and list updated files.

## Error handling

- **No meeting note** — Ask user which note to distill.
- **Note has no project** — Ask user which project to use.
- **Append-only** — Never overwrite past entries in People or Memory; always append.
