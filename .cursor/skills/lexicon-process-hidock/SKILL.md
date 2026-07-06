---
name: lexicon-process-hidock
description: HiDock pipeline sync-transcribe-summarize-distill via pending list (not date-based). Use when user says "process my HiDock meetings", "process hidock", or plug-in device workflow.
---

# Process HiDock meetings

Sync from device, transcribe, summarize each **pending** transcript, optionally distill.

Selection is **not date-based** — use transcripts that have no meeting note yet.

## Prerequisites

- **hinotes_organizer** (separate repo) — install per `docs/SETUP.md` § HiDock in your Lexicon vault:
  - `output.dir` → this vault's `Transcripts/HiDock/` (absolute path)
  - `markdown.save_segments_json: false` (skip the `.segments.json` sidecar + `segments_file:` frontmatter)
  - **Multi-language meetings:** constrain language detection rather than hardcoding — e.g. `transcription.language_detection_options.expected_languages: [en, ja]` + `fallback_language: en` + `language_confidence_threshold: 0.7`. Bare auto-detect can mis-detect the language; hardcoding one language breaks meetings held in the other.
  - `secrets.assemblyai_api_key` set
- **Lexicon `.env`:** `HIDOCK_ORGANIZER_ROOT=/path/to/hinotes_organizer`
- Run `python scripts/verify_setup.py` — HiDock section should be OK before first fetch

## Steps

1. **Init** — `python scripts/lexicon_init.py` (safe to re-run).

2. **Fetch** — Device plugged in, HiNotes/Chrome closed:
   ```bash
   python scripts/hidock_collection.py run
   ```
   Use `--limit N` when testing. Re-run anytime; organizer state skips finished files.

3. **List pending** — Transcripts without a meeting note:
   ```bash
   python scripts/hidock_pending.py list
   python scripts/hidock_pending.py list --json
   ```
   A transcript is **not** pending once any `Meetings/**/*.md` references it (wikilink to `Transcripts/HiDock/...` or frontmatter `hidock_signature:`).

4. **Summarize** — For each pending file:
   - Read transcript under `Transcripts/HiDock/`.
   - **Project:** infer from content + `Metadata/project_registry.md` (HiDock transcripts have no `project` field). Ask if unclear.
   - Create `Meetings/<Project>/YYYY-MM-DD [Title].md` per `.cursor/rules/summarize.mdc`.
   - Set meeting note `source: HiDock` and `hidock_signature: <signature>` from transcript frontmatter.
   - **Transcript Link:** wikilink to source file (basename without `.md` is enough).
   - **Speaker labels** — After attributions are clear (from dialogue: names spoken, roles, meeting note participants), **write back to the source transcript** per summarize rule (replace `Speaker N:` with `Full Name:`, add `participants:` to frontmatter). Skip write-back only if still uncertain — then leave a Context note on the meeting note.
   - Skip if a meeting note already references this transcript.

5. **Distill** — For each new meeting note (when user wants full pipeline):
   - Apply `.cursor/rules/distill.mdc` — evidence only.
   - Fill `# Distilled` on the meeting note.

6. **Report** — Organizer run result, pending count before/after, notes created, memory updated.

## Error handling

- **HIDOCK_ORGANIZER_ROOT / config missing** — Relay stderr; point to `docs/SETUP.md` § HiDock.
- **USB locked** — Close HiNotes/Chrome, replug device.
- **USB sync reports 0 new but device has files** — Re-run with device plugged in, HiNotes closed; if still stuck, run organizer `pipeline.py list` directly with full USB access.
- **Transcript in wrong language** — Check organizer `config.yaml` has `language_detection_options` + `language_confidence_threshold` (see Prerequisites); re-transcribe via hinotes_organizer if audio is still cached.
- **No pending after fetch** — Normal. Say "No new HiDock transcripts to summarize."
- **Multiple projects on one device** — Expected; assign project per transcript at summarize time.

## Related

- Single transcript: **lexicon-summarize** skill.
- Fireflies (date + account): **lexicon-process** skill — separate workflow.
