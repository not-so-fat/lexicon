# Transcripts

Raw meeting transcripts before summarize.

## Layout

```
Transcripts/
  Fireflies/<account>/     # Fetched from Fireflies (default: Transcripts/Fireflies/personal/)
  Manual/                  # Manual / HiNotes paste targets (project in frontmatter)
```

Do **not** nest another `Transcripts/` under `Fireflies/` or `Manual/`. If you need a custom Fireflies output path, set `OUTPUT_DIR_<account>` in `.env` — but prefer the default above.
