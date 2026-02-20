---
name: lexicon-manual-template
description: Create a manual transcript template file. Use when user says "create a manual transcript", "add a transcript", "new transcript template", or wants a file to paste meeting notes into.
---

# Create manual transcript template

Creates `Transcripts/Manual/YYYY-MM-DD_<slug>_manual.md` with frontmatter. User pastes transcript, then asks to summarize.

## Inputs

- **date** — YYYY-MM-DD or "today"
- **title** — e.g. "Catch up Satish"
- **with_whom** — person name
- **project** — personal, company, career, general

If any are missing, ask for them.

## Steps

1. Run from repo root:
   ```
   python scripts/manual_ingest.py --stub --date YYYY-MM-DD --title "Title" --with-whom "Name" --project <project>
   ```
2. Tell user: "Open `<path>`, paste your transcript under **# Raw Transcript**, save. Then ask me to **summarize this transcript**."

## Notes

- This skill only creates the file. Summarize is a separate step.
