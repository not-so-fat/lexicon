# Lexicon

**AI-ready organizational memory from meeting transcripts.**

Your Cursor agent turns transcripts (Fireflies, HiDock, manual, or pasted) into structured Markdown along four tiers that **are** the directory tree: `Sources/` (write-once captures) → `Evidence/` (append-only dated facts) → `Synthesis/` (what it adds up to, rewritten in triage) → `Direction/` + `Objectives.md` (constant input, curated in review). So you can query naturally: "What did we agree with Sarah?" No new app, no extra LLM API — your agent runs this repo's scripts and skills when you ask.

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

1. **Ingest** — after meetings: *"Process my Fireflies meetings for today"* / *"Process my HiDock meetings"* / paste into a manual template. Transcripts land under `Sources/Transcripts/`, meeting notes under `Sources/Meetings/<area>/`.
2. **Check** — skim the meeting note; fix speaker labels or area if the agent guessed wrong.
3. **Distill** — *"Distill this meeting note."* Facts append to `Evidence/<area>/` logs (append-only, one dated line per fact; nothing is synthesized yet) and lint what they touched.
4. **Triage (weekly-ish)** — *"Triage [area]."* Interactive recap: you and the agent review recent evidence and the Ideas queue, rewrite `Synthesis/<area>.md`, update open-decision files, and stage `## Direction candidates` for review. See [docs/MEMORY_MODEL.md](docs/MEMORY_MODEL.md).
5. **Query anytime** — just ask in Cursor: *"What do we know about pricing?"*, *"Prepare me for a meeting with Alex"*, *"What decisions did we make last month?"* The agent reads Direction → Synthesis → Evidence → Sources, most-distilled first.
6. **Review (weekly)** — *"Review my objectives."* Cross-area session: re-anchor on what you're trying to make true, read the evidence, retire what's done or missed. Max 5 objectives across all areas, one named WIG. See [docs/OBJECTIVES.md](docs/OBJECTIVES.md).

Capture your own thoughts as files under `Sources/Ideas/<area>/` — they enter the triage queue automatically until marked `triaged`.

---

## What it does

- **Fetch** – Fireflies by date/account; HiDock via hinotes_organizer (pending list); or manual template.
- **Summarize** – Raw transcript → structured meeting note (Context, Summary, Decisions, Action Items, Unresolved Points, Signals, AI Evaluation).
- **Distill** – Meeting note → durable **evidence** in `Evidence/<area>/` (Product, Org, Me, Validation, Partners, People). Evidence only — no synthesis; lints its own output.
- **Triage** – Interactive session you kick when ready: recap recent work, rewrite `Synthesis/<area>.md`, keep decision-state files honest, clean the **Ideas/Clippings** queue, write recap log. See [docs/MEMORY_MODEL.md](docs/MEMORY_MODEL.md).
- **Review** – Weekly cross-area session over **intent**, not truth: re-anchor on your objectives, read their evidence, retire what's done or missed. No score — the agent proposes `moving` / `stalled` / `drifting`, you decide. See [docs/OBJECTIVES.md](docs/OBJECTIVES.md).

Philosophy: prefer recall over compression; notes are evidence. Early-stage signals matter — preserve them. Synthesis happens in **triage**, not distill.

---

## Where things live

| What | Path |
|------|------|
| Transcripts | `Sources/Transcripts/Fireflies/<account>/`, `…/HiDock/`, `…/Manual/` |
| Meeting notes | `Sources/Meetings/<area>/` |
| Ideas / Clippings | `Sources/Ideas/<area>/`, `Sources/Clippings/` (empty `triaged:` = in queue) |
| Evidence (per area) | `Evidence/<area>/` (Product, Org, Me, Validation, `Partners/`, `People/`) |
| Synthesis (per area) | `Synthesis/<area>.md`, decision files in `Synthesis/<area>/decisions/` |
| Direction (per area) | `Direction/<area>.md`, lenses in `Direction/Lenses/` |
| Objectives (all areas) | `Objectives.md`, `Objectives.evidence.md` |
| Triage recap logs | `Metadata/recap/<area>/YYYY-MM.md` |
| Review logs | `Metadata/review/YYYY-Www.md` |
| Usage telemetry | `Metadata/usage/access.jsonl` (gitignored) |
| Scratch / logs | **`.tmp/`** only |

---

## Skills (what you say)

| Say | Skill does |
|-----|------------|
| "Process my Fireflies meetings for [date] on my [account] account" | Fetch → summarize → distill |
| "Process my HiDock meetings" | Sync → pending list → summarize → distill |
| "Create a manual transcript template" | Stub in `Transcripts/Manual/` |
| "Summarize this transcript" | Meeting note at `Sources/Meetings/<area>/` |
| "Distill this meeting note" | Append evidence bullets; fill `# Distilled`; lint |
| "Triage \<area\>" or "Recap \<area\>" | Interactive recap, rewrite `Synthesis/<area>.md`, clean Ideas queue |
| "Review my objectives" / "weekly review" | Cross-area objectives review; retire and re-anchor |

Skills: `.cursor/skills/`. Rules: `.cursor/rules/`.

```bash
python3 scripts/triage_queue.py --area <area> [--since YYYY-MM-DD]
python3 scripts/review_queue.py
python3 scripts/lint_vault.py
python3 scripts/hidock_pending.py list
python3 scripts/verify_setup.py
```

---

## Docs

| Doc | What it covers |
|-----|----------------|
| [docs/SETUP.md](docs/SETUP.md) | Full install: Fireflies, HiDock (hinotes_organizer), manual |
| [docs/MEMORY_MODEL.md](docs/MEMORY_MODEL.md) | The four tiers, per-directory contracts, schemas, decision files, QA |
| [docs/OBJECTIVES.md](docs/OBJECTIVES.md) | The normative tier: horizons, the cap and the WIG, the weekly review, why there is no score |
| [docs/UPDATING.md](docs/UPDATING.md) | Pulling engine updates without touching your content; `local-*.mdc` customization |
| `Direction/Lexicon.md` | Direction file: the two loops, the stages and the write boundaries |

---

## License

MIT. See [LICENSE](LICENSE).
