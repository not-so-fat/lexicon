---
name: lexicon-summarize
description: Creates a Lexicon meeting note from a raw transcript file. Use when the user asks to "summarize this transcript", "create a meeting note from this transcript", or points at a transcript under Transcripts/ and wants it turned into a structured meeting note at Meetings/<Project>/.
---

# Lexicon: Summarize transcript → meeting note

Turns one raw transcript (Fireflies, HiNotes, or manual) into a structured meeting note under `Meetings/<Project>/`.

## When to use

User says things like:
- "Summarize this transcript"
- "Create a meeting note from this transcript"
- "Turn this into a meeting note"
- Points at or @-mentions a file under `Transcripts/Fireflies/` or `Transcripts/Manual/`

If the transcript file is unclear, ask which file to use.

**Manual transcripts:** Summarize only works on an existing transcript file. If the user has pasted text or has no file yet, do not create the file in this skill. Use the **lexicon-manual-template** skill instead: it creates a template file under `Transcripts/Manual/`. Tell the user to ask for that ("Create a manual transcript template" or "I want to add a manual transcript"), then edit the file (paste under "# Raw Transcript"), save, then ask to summarize.

## Steps

1. **Identify the transcript**  
   Path under `Transcripts/Fireflies/<account>/` or `Transcripts/Manual/`. Read its frontmatter (title, date, participants or with_whom, source, project).

2. **Choose project**  
   Use only `project` from the transcript frontmatter. Do not infer project from the path. If frontmatter has no project, ask the user which project (personal, company, career, general) to use.

3. **Create meeting note**  
   Path: `Meetings/<Project>/YYYY-MM-DD [Title].md`.  
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
