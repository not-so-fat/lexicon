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

2. **Fetch** — Resolve date, then run:
   ```bash
   python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>
   ```
   - This step may be re-run during the day; it just syncs new transcripts into `Transcripts/Fireflies/<account>/`.
   - Do **not** decide what to summarize based on the `fireflies_YYYY-MM-DD_<account>.log` date or file name prefixes.

3. **Select transcripts to summarize (by frontmatter date, not filename)**  
   For the requested `date`:
   - Search `Transcripts/Fireflies/<account>/` for files whose **frontmatter** contains:
     ```yaml
     date: YYYY/MM/DD
     ```
   - Filter to `project: <project>` (or ask the user which project if missing).
   - This selection is based **only on the `date:` field**, not on which `process-date` command produced the file or what date appears in the filename.  
   - This avoids missing meetings when Fireflies saves a `2026-03-10_*.md` file during a `process-date 2026-03-11` run.

   A simple way to find candidate files for a given date is:
   ```bash
   rg "^date:\s*YYYY/MM/DD" "Transcripts/Fireflies/<account>/" --glob "*.md" --files-with-matches
   ```
   Then, for each matching file, read the frontmatter and confirm `project: <project>` before summarizing.

4. **Summarize** — For each matching transcript:
   - If a meeting note for `(project, date, title)` does **not** exist:
     - Create `Meetings/<Project>/YYYY-MM-DD [Title].md` following `.cursor/rules/summarize.mdc`.
   - If it already exists, only re-summarize when the user explicitly asks to refresh.

5. **Distill** — For each new meeting note:
   - Apply `.cursor/rules/distill.mdc`.
   - Fill the note's **# Distilled** section with links to updated files.

6. **Report** — Tell user: transcripts fetched, notes created, memory updated.

## Error handling

- **No .env or missing key** — Script prints a clear message. Relay it and suggest checking `.env.example`.
- **No transcripts for that date** — Normal. Say "No meetings found" and stop.
- **Missing `project` in frontmatter** — Ask user which project to use for this run.
