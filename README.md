# Lexicon

**AI-ready organizational memory from meeting transcripts.**

Your Cursor agent turns transcripts (Fireflies, HiDock, manual, or pasted) into structured Markdown: meeting notes → People, Product, and Org memory — then **triage** keeps current truth fresh and cleans your Ideas queue. So you can query naturally: "What did we agree with Sarah?" No new app, no extra LLM API — your agent runs this repo's scripts and skills when you ask.

---

## Installation

**Full guide:** [docs/SETUP.md](docs/SETUP.md)

```bash
git clone <url-to-lexicon> lexicon
cd lexicon
cp .env.example .env          # set LEXICON_USER_NAME at minimum
pip install -r requirements.txt
python scripts/lexicon_init.py
python scripts/verify_setup.py
```

Open the folder in **Cursor**. Add Fireflies and/or HiDock when you need them — see [SETUP.md](docs/SETUP.md).

Your clone **is** your vault: content stays local/private, engine updates pull from this repo — see [docs/UPDATING.md](docs/UPDATING.md). Customize via `.cursor/rules/local-*.mdc`, not by editing shipped rules.

| You use | Also configure |
|---------|----------------|
| Fireflies | `FIREFLIES_API_KEY_*`, `EMAIL_*` in `.env` |
| HiDock P1 | [hinotes_organizer](docs/SETUP.md#3-hidock-optional) + `HIDOCK_ORGANIZER_ROOT` in `.env` |
| Manual paste only | Nothing else |

---

## Quick start (after install)

**Fireflies** — *"Process my Fireflies meetings for today on my personal account."*

**HiDock** — plug device, quit HiNotes, then *"Process my HiDock meetings."*

**Manual** — *"Create a manual transcript template."* Paste transcript → *"Summarize this transcript"* → *"Distill this meeting note."*

---

## Daily loop (user guide)

1. **Ingest** — after meetings: *"Process my Fireflies meetings for today"* / *"Process my HiDock meetings"* / paste into a manual template. Transcripts land under `Transcripts/`, meeting notes under `Meetings/<Project>/`.
2. **Review** — skim the meeting note; fix speaker labels or project if the agent guessed wrong.
3. **Distill** — *"Distill this meeting note."* Facts append to People pages and Memory evidence logs (append-only, one line per fact; nothing is synthesized yet).
4. **Triage (weekly-ish)** — *"Triage [project]."* Interactive recap: you and the agent review recent evidence and the Ideas queue, and only here does `# Current model` get updated. See [docs/MEMORY_MODEL.md](docs/MEMORY_MODEL.md).
5. **Query anytime** — just ask in Cursor: *"What do we know about pricing?"*, *"Prepare me for a meeting with Alex"*, *"What decisions did we make last month?"* The agent searches Memory → People → Meetings, most-distilled first.

Capture your own thoughts as files under `Ideas/<Project>/` — they enter the triage queue automatically until marked `triaged`.

---

## What it does

- **Fetch** – Fireflies by date/account; HiDock via hinotes_organizer (pending list); or manual template.
- **Summarize** – Raw transcript → structured meeting note (Context, Summary, Decisions, Action Items, Unresolved Points, Signals, AI Evaluation).
- **Distill** – Meeting note → durable **evidence** in `People/<Project>/`, `Memory/<Project>/`. Evidence only — no synthesis.
- **Triage** – Interactive session you kick when ready: recap recent work, update **current truth** in Memory, clean **Ideas/Clippings** queue, write recap log. See [docs/MEMORY_MODEL.md](docs/MEMORY_MODEL.md).

Philosophy: prefer recall over compression; notes are evidence. Early-stage signals matter — preserve them. Synthesis happens in **triage**, not distill.

---

## Where things live

| What | Path |
|------|------|
| Transcripts | `Transcripts/Fireflies/<account>/`, `Transcripts/HiDock/`, `Transcripts/Manual/` |
| Meeting notes | `Meetings/<Project>/` |
| People / Memory | `People/<Project>/`, `Memory/<Project>/` |
| Ideas / Clippings | `Ideas/<Project>/`, `Clippings/` (empty `triaged:` = in queue) |
| Triage recap logs | `Metadata/recap/<Project>/YYYY-MM.md` |
| Process charter | `Memory/Lexicon/processing-strategy.md` |
| Scratch / logs | **`.tmp/`** only |

---

## Skills (what you say)

| Say | Skill does |
|-----|------------|
| "Process my Fireflies meetings for [date] on my [account] account" | Fetch → summarize → distill |
| "Process my HiDock meetings" | Sync → pending list → summarize → distill |
| "Create a manual transcript template" | Stub in `Transcripts/Manual/` |
| "Summarize this transcript" | Meeting note at `Meetings/<Project>/` |
| "Distill this meeting note" | Append evidence bullets; fill `# Distilled` |
| "Triage \<project\>" or "Recap \<project\>" | Interactive recap, update Memory current truth, clean Ideas queue |

Skills: `.cursor/skills/`. Rules: `.cursor/rules/`.

```bash
python3 scripts/triage_queue.py --project <project> [--since YYYY-MM-DD]
python3 scripts/lint_vault.py
python3 scripts/hidock_pending.py list
python3 scripts/verify_setup.py
```

---

## Docs

| Doc | What it covers |
|-----|----------------|
| [docs/SETUP.md](docs/SETUP.md) | Full install: Fireflies, HiDock (hinotes_organizer), manual |
| [docs/MEMORY_MODEL.md](docs/MEMORY_MODEL.md) | How knowledge is organized: evidence vs current model, layouts, triage |
| [docs/UPDATING.md](docs/UPDATING.md) | Pulling engine updates without touching your content; `local-*.mdc` customization |
| `Memory/Lexicon/processing-strategy.md` | Process charter: the five-stage pipeline and triage discipline |

---

## License

MIT. See [LICENSE](LICENSE).
