---
name: lexicon-manual-template
description: Creates an empty manual transcript file (template) under Transcripts/Manual/ so the user can paste or type their transcript, then run summarize. Use when the user wants to add a manual or HiNotes transcript and needs a file to edit.
---

# Lexicon: Create manual transcript template

Creates a stub file at `Transcripts/Manual/YYYY-MM-DD_<slug>_manual.md` with frontmatter and a "# Raw Transcript" section. The user edits the file (paste transcript), then asks to summarize.

## When to use

User says things like:
- "I want to add a manual transcript"
- "Create a template for a HiNotes transcript"
- "I need a file to paste my meeting transcript into"
- "Set up a new manual transcript for me"

## Steps

1. **Gather inputs.** You need: **date** (YYYY-MM-DD), **title** (e.g. "Catch up Satish" or meeting title), **with_whom**, **project** (personal, company, career, general).  
   If the user gave them, use those. If not, ask: "What date (YYYY-MM-DD), title (or 'Catch up [name]'), with whom, and project (personal, company, career, general)?"  
   For date, if they say "today" use current date in YYYY-MM-DD.

2. **Create the file.** From the repo root, run:
   `python scripts/manual_ingest.py --stub --date YYYY-MM-DD --title "Title" --with-whom "Name" --project <project>`
   Use the exact date, title, with_whom, and project. If title has spaces or special characters, quote it.

3. **Reply.** Tell the user the path of the created file (e.g. `Transcripts/Manual/2026-02-17_Catch_up_Satish_manual.md`). Say: "Open that file, paste your transcript under **# Raw Transcript**, save. Then ask me to **summarize this transcript** and I'll create the meeting note."

## Notes

- This skill only creates the template. The user edits the file; then they use the **lexicon-summarize** skill to create the meeting note.
- One-off or scratch output goes in `.tmp/` only.
