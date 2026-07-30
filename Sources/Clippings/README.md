# Clippings

Web clips, references, and external material tagged to an area.

## Convention

- Tag each file with **`area:`** and **`created:`** in frontmatter.
- Empty **`triaged:`** = still in the triage queue (same as `Ideas/`).

## Template

Copy from `.cursor/templates/clipping_template.md`.

## Processing

Review and route in **triage** — Promote (durable fact → `Evidence/`, via the
session), Keep editing, Skip, Retire, or Move.

```bash
python3 scripts/triage_queue.py --area <area>
```
