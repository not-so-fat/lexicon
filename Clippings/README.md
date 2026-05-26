# Clippings

Web clips, references, and external material tagged to a project.

## Convention

- Tag each file with **`project:`** and **`created:`** in frontmatter.
- Empty **`triaged:`** = still in the triage queue (same as `Ideas/`).

## Template

Copy from `.cursor/templates/clipping_template.md`.

## Processing

Review and route in **triage** — Promote to Memory, Keep editing, Skip, Retire, or Move.

```bash
python3 scripts/triage_queue.py --project <project>
```
