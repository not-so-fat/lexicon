---
name: lexicon-process
description: Full Fireflies pipeline fetch-summarize-distill for one date and account. Use when user says "process my Fireflies meetings", "fetch and summarize", or mentions a date and Fireflies account.
---

# Process Fireflies meetings

Fetch transcripts for a date + account, summarize each, distill each.

## Inputs

- **date** — YYYY-MM-DD, "today", or "yesterday"
- **account** — matches .env suffix (e.g. personal, acme)

If either is missing, ask: "Which date and which account?"

## Steps

1. **Init** — `python scripts/lexicon_init.py` (safe to re-run).
2. **Fetch** — Resolve date, then:
   ```
   python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>
   ```
   If no new transcripts, tell user and stop.
3. **Summarize** — For each new transcript in `Transcripts/Fireflies/<account>/`:
   - Read `project` from frontmatter. If missing, ask user.
   - Create `Meetings/<Project>/YYYY-MM-DD [Title].md` following `.cursor/rules/summarize.mdc`.
4. **Distill** — For each new meeting note:
   - Apply `.cursor/rules/distill.mdc`.
   - Fill the note's **# Distilled** section with links to updated files.
5. **Report** — Tell user: transcripts fetched, notes created, memory updated.

## Error handling

- **No .env or missing key** — Script prints a clear message. Relay it and suggest checking `.env.example`.
- **No transcripts for that date** — Normal. Say "No meetings found" and stop.
- **Missing `project` in frontmatter** — Ask user which project to use for this run.
