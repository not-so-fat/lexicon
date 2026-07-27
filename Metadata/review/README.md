# Review logs

Written by **review** — one file per ISO week, global across all areas:

`Metadata/review/YYYY-Www.md`

Each weekly review appends a section recording the status proposed and accepted per objective (`moving` / `stalled` / `drifting` — never a score), retirements with their outcomes, anything routed out to `Direction/<area>.md` or out of the vault, and the WIG for the coming week.

Before review:

```bash
python3 scripts/review_queue.py
```

Output: **cap and WIG state**, per-objective horizon and evidence staleness, past-horizon objectives, days since the last review. Signals only — the verdict is yours. See [../../docs/OBJECTIVES.md](../../docs/OBJECTIVES.md).
