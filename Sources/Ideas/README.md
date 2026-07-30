# Ideas

Scratch notes and thinking captures. **Not** meeting evidence — use `Sources/Meetings/` for that.

## Convention

- One folder per area: `Sources/Ideas/<area>/` (and tag files with `area:` in frontmatter).
- At capture: set **`area`** and **`created`** only.
- Empty **`triaged:`** = still in the triage queue.
- Nothing lives here permanently — at triage, every idea is **promoted or deleted**
  (git preserves history). Large normative documents (lenses) are iterated here,
  then promoted in **review**.

## Template

Copy from `.cursor/templates/ideas_template.md` when creating a new idea.

## Processing

Meetings: **Summarize → Distill** (automated or per-note).

Ideas: **Triage** when you are ready — interactive session; see `Direction/Lexicon.md`.

```bash
python3 scripts/triage_queue.py --area <area>
```
