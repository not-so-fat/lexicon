---
name: lexicon-summarize
description: Creates a Lexicon meeting note from a raw transcript file. Use when the user asks to "summarize this transcript", "create a meeting note from this transcript", or points at a transcript under Transcripts/ and wants it turned into a structured meeting note at Meetings/<Area>/.
---

# Lexicon: Summarize transcript → meeting note

Turns one raw transcript (Fireflies, HiNotes, or manual) into a structured meeting note under `Meetings/<Area>/`.

## When to use

User says things like:
- "Summarize this transcript"
- "Create a meeting note from this transcript"
- "Turn this into a meeting note"
- Points at or @-mentions a file under `Transcripts/Fireflies/` or `Transcripts/Manual/`

If the transcript file is unclear, ask which file to use.

**If the user pastes transcript text** and says "add this transcript and summarize" (or similar) and there is no transcript file yet: create a transcript file first. Ask for **date** (YYYY-MM-DD), **title** (or "Catch up [name]"), **with_whom**, and **area** (work, personal, career, general). Create `Transcripts/Manual/<Area>/YYYY-MM-DD_<slug>_manual.md` with frontmatter and the pasted content under "# Raw Transcript", then continue with the steps below to create the meeting note.

## Steps

1. **Identify the transcript**  
   Path under `Transcripts/Fireflies/<account>/` or `Transcripts/Manual/<Area>/`. Read its frontmatter (title, date, participants or with_whom, source, area if present).

2. **Choose area**  
   Use `area` from frontmatter, or infer from path (e.g. `Transcripts/Manual/work/` → area work). Defaults: work, personal, career, general.

3. **Create meeting note**  
   Path: `Meetings/<Area>/YYYY-MM-DD [Title].md`.  
   Follow the **exact structure and sections** in `.cursor/rules/summarize.mdc` (frontmatter, # Analysis, # Key Learnings & Decisions, # Action Items, # Transcript Link, # Distilled). Do not duplicate the full rule; apply it.

4. **Transcript Link**  
   In the meeting note, link to the raw transcript file path.

5. **Distilled**  
   Leave empty or: "(Run **distill** after reviewing this summary.)"

6. **Reply**  
   Tell the user the meeting note path and suggest reviewing (especially speaker attribution for HiNotes) before distilling.

## Notes

- HiNotes transcripts have no speaker labels; note in the summary when attribution is inferred and suggest review before distill.
- Do not update People/Memory/Metadata here; that is the distill step.
- Scratch/temporal output goes in `.tmp/` only.
