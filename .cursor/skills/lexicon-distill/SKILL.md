---
name: lexicon-distill
description: Distills a Lexicon meeting note into People, Memory, and Metadata. Use when the user asks to "distill this meeting note", "distill this note", or wants to extract durable knowledge from a meeting note at Meetings/<Area>/ into People/<Area>/, Memory/<Area>/, and Metadata/.
---

# Lexicon: Distill meeting note → People / Memory / Metadata

Updates `People/<Area>/`, `Memory/<Area>/`, and `Metadata/` from one meeting note, and fills the note's **# Distilled** section.

## When to use

User says things like:
- "Distill this meeting note"
- "Distill this note"
- "Extract knowledge from this meeting"
- Points at or @-mentions a file under `Meetings/<Area>/`

If the meeting note is unclear, ask which file to use.

## Steps

1. **Identify the meeting note**  
   Path under `Meetings/<Area>/`. Read it; the note is the source of truth (user may have edited it).

2. **Apply distill rule**  
   Follow `.cursor/rules/distill.mdc` in full:
   - Decide deep vs light distillation.
   - Update **People/<Area>/[Name].md** (Catch-up Log, Communication Style, etc.).
   - Update **Memory/<Area>/** (Product, Org, Partnerships, Career, Technical as needed).
   - Update **Metadata/CommunicationStyle.md** and **Metadata/CurrentPriorities.md** when relevant.
   - For external/experienced-person meetings, add learnings and feedback as in the rule.

3. **Traceability**  
   In the meeting note's **# Distilled** section, list every destination you actually updated (links to People, Memory, Metadata files/sections). Overwrite that section with the new list.

4. **Reply**  
   Confirm distillation done and list the updated files/sections.

## Notes

- Do not re-parse the raw transcript unless needed to clarify something in the note.
- Never overwrite past bullets in People pages; append or refine.
- Scratch/temporal output goes in `.tmp/` only.
