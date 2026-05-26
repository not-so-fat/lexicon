# Recap logs

Written by **triage** — one file per month per project:

`Metadata/recap/<project>/YYYY-MM.md`

Each triage run appends a `## YYYY-MM-DD triage` section (conversation recap, memory updates, ideas actions, pending decisions).

Before triage:

```bash
python3 scripts/triage_queue.py --project <project> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
```

Output: **ideas queue** + **recent meetings (read-only recap context)** + pending decisions. Meetings are **not** in the queue — distill handles them separately.
