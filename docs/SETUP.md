# Lexicon setup

One vault (this repo or your Obsidian copy), three transcript sources. Configure only what you use.

| Source | Ingest | Summarize trigger |
|--------|--------|-------------------|
| **Fireflies** | API by date + account | "Process my Fireflies meetings for …" |
| **HiDock** | USB device via hinotes_organizer | "Process my HiDock meetings" |
| **Manual** | Paste into template file | "Summarize this transcript" |

---

## Prerequisites

| Tool | Fireflies | HiDock | Manual |
|------|-----------|--------|--------|
| Python 3.10+ | yes | yes | yes |
| Cursor (agent + skills) | yes | yes | yes |
| `pip install -r requirements.txt` | yes | yes | yes |
| Fireflies API key | yes | — | — |
| HiDock P1 + macOS | — | yes | — |
| [hinotes_organizer](#3-hidock-optional) (separate repo) | — | yes | — |
| Node.js 22+ + libusb (HiDock USB) | — | yes | — |
| AssemblyAI API key (in organizer config) | — | yes* | — |

\* Default HiDock path uses cloud transcription. Local GPU transcription is optional in hinotes_organizer.

---

## 1. Lexicon (everyone)

From your vault / repo root:

```bash
cp .env.example .env
```

Edit `.env` — minimum:

```bash
LEXICON_USER_NAME=Your Name
```

Install Python deps and create folders:

```bash
pip install -r requirements.txt
python scripts/lexicon_init.py
python scripts/verify_setup.py
```

Open the folder in **Cursor**. Skills live in `.cursor/skills/`; the agent uses them when you ask in natural language.

**Verify:** `verify_setup.py` should report core folders and `LEXICON_USER_NAME` as OK.

---

## 2. Fireflies (optional)

In `.env`:

```bash
FIREFLIES_API_KEY_personal=ff_...
EMAIL_personal=you@example.com
PROJECT_personal=personal
```

Add more accounts with suffix `_work`, `_acme`, etc. See `.env.example`.

**Test fetch** (use a date you have meetings, or an empty day):

```bash
python scripts/fireflies_collection.py process-date 2026-01-15 personal
```

Transcripts land in `Transcripts/Fireflies/<account>/`.

**Agent:** *"Process my Fireflies meetings for 2026-01-15 on my personal account."*

---

## 3. HiDock (optional)

HiDock needs **two repos**: Lexicon (this vault) and **hinotes_organizer** (device + transcribe). Lexicon does not embed USB logic.

### 3a. Install hinotes_organizer

```bash
git clone <url-to-hinotes_organizer> ~/codes/hinotes_organizer
cd ~/codes/hinotes_organizer
brew install libusb          # macOS USB
chmod +x scripts/setup.sh
./scripts/setup.sh
cp config.example.yaml config.yaml
```

Edit `config.yaml`:

```yaml
output:
  dir: /absolute/path/to/your/vault/Transcripts/HiDock

secrets:
  assemblyai_api_key: "your-key-from-assemblyai-dashboard"

transcription:
  language_detection_options:
    expected_languages: ["en", "ja"]   # the languages your meetings are actually in
    fallback_language: en
  language_confidence_threshold: 0.7

markdown:
  save_segments_json: false   # Lexicon uses .md only
```

If your meetings span multiple languages, use constrained language detection as above. Bare auto-detect can mis-label the language (e.g. English audio transcribed as another language); hardcoding one `language:` breaks meetings held in the other.

> [!important] `config.yaml` does not sync between machines
> `hinotes_organizer/config.yaml` is gitignored (it holds the API key). On a new machine recreate it by hand — `output.dir`, `language_detection_options`, `language_confidence_threshold`, and `save_segments_json: false` are all required; omitting them silently reintroduces past bugs.

Get an AssemblyAI key: https://www.assemblyai.com/dashboard

**Test organizer alone** (HiDock plugged in, HiNotes/Chrome **closed**):

```bash
source .venv/bin/activate
python scripts/pipeline.py run --limit 1
```

You should see a new `.md` file under `Transcripts/HiDock/` in your vault.

### 3b. Connect Lexicon

In Lexicon `.env`:

```bash
HIDOCK_ORGANIZER_ROOT=/absolute/path/to/hinotes_organizer
# optional override:
# HIDOCK_CONFIG=/path/to/config.yaml
```

Re-run verification:

```bash
python scripts/verify_setup.py
```

HiDock section should show: organizer repo OK, `output.dir` matches `Transcripts/HiDock/`, API key present.

### 3c. Daily workflow

```bash
# From Lexicon repo root — device plugged in, HiNotes closed
python scripts/hidock_collection.py run

# What still needs a meeting note?
python scripts/hidock_pending.py list
```

**Agent:** *"Process my HiDock meetings"* — sync, list pending, summarize each, optionally distill.

**Notes:**
- One HiDock device can feed **multiple projects** — project is chosen at **summarize** time, not in organizer config.
- Transcripts start as `Speaker N:` — the agent writes back full names during summarize when confident; review before distill.
- Selection is **pending-based**, not by date.

### HiDock troubleshooting

| Problem | Fix |
|---------|-----|
| `HIDOCK_ORGANIZER_ROOT not set` | Add to Lexicon `.env` |
| `output.dir mismatch` | Set organizer `output.dir` to vault `Transcripts/HiDock/` (absolute path) |
| `LIBUSB_ERROR_ACCESS` | Quit HiNotes / Chrome using the device; replug |
| No new files after `run` | Device empty or already transcribed (organizer state skips done files) |
| `assemblyai_api_key` missing | Set under `secrets:` in organizer `config.yaml` |
| Transcript in the **wrong language** | Usually missing `language_detection_options` / threshold in `config.yaml` (common on a new machine). Add the block from 3a; re-transcribe via hinotes_organizer if audio is still cached |
| Wrong `Speaker N` labels | The agent writes back full names during summarize (see lexicon-summarize skill), or edit the transcript manually before distill |

Optional automation: hinotes_organizer `scripts/run_pipeline.sh` + macOS LaunchAgent (see hinotes_organizer README).

---

## 4. Manual transcripts (optional)

No extra install. Ask the agent: *"Create a manual transcript template"* with date, title, with whom, project.

Or:

```bash
python scripts/manual_ingest.py --stub --date 2026-01-15 --title "Catch up" \
  --with-whom "Alex" --project personal
```

Paste under `# Raw Transcript`, then *"Summarize this transcript"*.

---

## 5. After ingest — summarize & distill

Same for all sources:

1. **Summarize** → `Meetings/<Project>/YYYY-MM-DD Title.md`
2. **Review** the note (especially HiDock speaker labels)
3. **Distill** → append `# Evidence` to People / Memory
4. **Triage** (later) → update `# Current model` in interactive sessions

---

## Checklist

- [ ] `.env` with `LEXICON_USER_NAME`
- [ ] `pip install -r requirements.txt`
- [ ] `python scripts/lexicon_init.py`
- [ ] `python scripts/verify_setup.py` — core OK
- [ ] (Fireflies) API key + email in `.env`
- [ ] (HiDock) hinotes_organizer installed + `output.dir` → `Transcripts/HiDock/`
- [ ] (HiDock) `HIDOCK_ORGANIZER_ROOT` in `.env`
- [ ] (HiDock) test `hidock_collection.py run --limit 1`
