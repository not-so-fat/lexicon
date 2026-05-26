# Ideas

Scratch notes and thinking captures. **Not** meeting evidence — use `Meetings/` for that.

## Convention

- One folder per project: `Ideas/<project>/` (or tag files with `project:` in frontmatter).
- At capture: set **`project`** and **`created`** only.
- Empty **`triaged:`** = still in the triage queue.

## Template

Copy from `.cursor/templates/ideas_template.md` when creating a new idea.

## Processing

Meetings: **Summarize → Distill** (automated or per-note).

Ideas: **Triage** when you are ready — interactive session; see `Memory/Lexicon/processing-strategy.md`.

```bash
python3 scripts/triage_queue.py --project <project>
```
