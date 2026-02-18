---
name: lexicon-process
description: Runs the full Lexicon pipeline for Fireflies: fetch transcripts for a date and account, then summarize each into a meeting note and distill each note into People/Memory/Metadata. Use when the user asks to "process" their Fireflies meetings. Accepts "today" or "yesterday" as date. Example: "Process my Fireflies meetings for today on my work account".
---

# Lexicon: Process Fireflies meetings

Runs **fetch → summarize → distill** for a given date and account. One pipeline from transcripts to memory.

## When to use

User says things like:
- "Process my Fireflies meetings for **today** on my work account"
- "Process my Fireflies meetings for 2026-02-17 on my personal account"
- "Process my meetings for yesterday, work account"
- "Fetch and summarize and distill my meetings for today, personal"

**Date:** If the user says **today**, use the current date in YYYY-MM-DD. If they say **yesterday**, use yesterday's date. Otherwise use the given date (YYYY-MM-DD).

**Account:** work, personal, or whatever name they use (must match an account in their .env).

If date or account is missing, ask: "Which date (e.g. today, 2026-02-17) and which account (e.g. work, personal)?"

## Steps

1. **Init (if needed)**  
   Ensure folder skeleton exists:
   `python scripts/lexicon_init.py`

2. **Fetch**  
   Resolve date: "today" → current date, "yesterday" → yesterday; else use given YYYY-MM-DD.  
   Run: `python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>`  
   Transcripts land in `Transcripts/Fireflies/<account>/`.

3. **Summarize**  
   For each **new** transcript file in that folder for that date: create a meeting note at `Meetings/<Area>/YYYY-MM-DD [Title].md` following the structure in `.cursor/rules/summarize.mdc`. Use the transcript's frontmatter (e.g. `area` or infer area from context). Do not duplicate the rule content; apply it.

4. **Distill**  
   For each meeting note you just created (or that was updated): update `People/<Area>/`, `Memory/<Area>/`, and `Metadata/` following `.cursor/rules/distill.mdc`, and fill the note's **# Distilled** section with links to every destination updated. Apply the rule; do not duplicate it.

5. **Report**  
   Tell the user how many transcripts were fetched, how many meeting notes created/updated, and that People/Memory/Metadata were updated.

## Notes

- If fetch returns no new transcripts, say so and skip summarize/distill for that run.
- Area comes from transcript frontmatter or user context; default areas are work, personal, career, general.
- All one-off or scratch output goes in `.tmp/`, not in Transcripts/Meetings/People/Memory/Metadata or `scripts/`.
