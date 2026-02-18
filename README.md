# Lexicon

**AI-ready organizational memory from meeting transcripts.**

Lexicon turns conversations into structured knowledge so you can prep for meetings, switch context, and mine insights—using **Cursor** and your own vault, not a new app.

---

## User story

**You:** Manager, founder, or anyone with many meetings. Transcripts live in Fireflies, HiNotes, or pasted notes. You lose context across people and projects; prep is ad hoc; there's no single place that "remembers" what was said and decided. Especially in early-stage startups, subtle signals—a customer's offhand comment, a partner's hesitation, a team member's concern—often matter later but get buried in transcripts.

**Lexicon:** Your **agent** (in Cursor) converts meeting transcripts into AI-ready memory—structured knowledge about **People**, **Product**, and **Org**, all in **Markdown** in this repo. The reason: so you can **query** naturally (“What did we agree with Sarah?” or “What’s the latest on the partnership with X?”) over that memory.

No new UI. No extra LLM API. Your agent runs the repo's scripts and skills when you ask.

---

## What Lexicon does

1. **Fetch** – Pull transcripts from Fireflies (by account and date) or add manual/HiNotes transcripts into a single structure.
2. **Summarize** – Turn a raw transcript into a structured meeting note: Context, Atmosphere, Summary, Decisions, Action Items, Unresolved Points, Signals (people/product/org/decision/risk/learning), Self-evaluation (Cursor + rules).
3. **Distill** – Turn a meeting note into durable memory: per-person pages (`People/<Project>/`), product/org learnings (`Memory/<Project>/`), and decisions (Cursor + rules).

That prepared memory is **why** you do this: so you (and Cursor) can query naturally over Transcripts, Meetings, People, and Memory—e.g. "What did we agree with Sarah?" All output is **local Markdown** with YAML frontmatter. The main consumer is **AI** (Cursor), not a dashboard.

**Philosophy:** Prefer recall over compression. Meeting notes preserve subtle, weak, or ambiguous statements—they're structured evidence, not summaries. Distillation extracts durable knowledge (append-only memory). Patterns emerge from history. Early-stage signals are often weak but critical; what seems minor today may shape decisions months later.

---

## Quick start (high level)

No extra step is needed to "install" Lexicon: your agent uses this repo's **scripts** and **skills** from the cloned folder. There is no global `lexicon` binary to install.

1. **Clone** this repo.
2. **Configure** – Copy `.env.example` to `.env`. Set **LEXICON_USER_NAME** (your name) first—needed for Self-evaluation and retrospectives in meeting notes. Then set Fireflies API key(s) and priority email(s) per account. Default account is **personal**; use company name for another (e.g. "acme"). If account name is not the project (e.g. "acme" but you want notes in company), set **PROJECT_acme=company**. Install Python deps: `pip install -r requirements.txt` (for fetch scripts).
3. **Fireflies (automated)** – You ask (e.g. "Process my Fireflies meetings for 2026-02-17 on my personal account"). The agent runs init (if needed), then **fetch → summarize → distill** using the repo skills. Transcripts land under `Transcripts/Fireflies/<account>/`; meeting notes under `Meetings/<Project>/`; People/Memory/Metadata are updated by the distill skill. (We call this full pipeline **process**.)
4. **HiNotes / manual transcripts** – You paste or ingest a transcript into `Transcripts/Manual/` and set **project** in frontmatter (no speaker labels). You ask (e.g. “Summarize this transcript into a meeting note”). The agent creates the note using the summarize skill. You **review** it (especially speaker attribution), then ask (e.g. “Distill this meeting note”). The agent updates People/Memory/Metadata using the distill skill.

See **Installation & configuration** below for setup details.

---

## How to: Fireflies (e.g. today)

**Goal:** Process all Fireflies meetings for a date (e.g. today) on one account: fetch → summarize → distill.

**What you do:**

1. Say exactly: **"Process my Fireflies meetings for today on my personal account"** (or use a date: "for 2026-02-17", or "yesterday"; use your account name: personal, acme, etc.).
2. The agent runs init (if needed), fetches transcripts for that date, creates a meeting note for each, and distills each note into People/Memory/Metadata.
3. Done. Transcripts are in `Transcripts/Fireflies/<account>/`, meeting notes in `Meetings/<Project>/`, memory updated.

If you have no meetings that day, the agent will say so and nothing is written.

---

## How to: Manual / HiNotes transcripts

**Goal:** Get a manual or HiNotes transcript (no Fireflies) into Lexicon and into memory: create transcript file → edit it → summarize → review → distill.

**What you do:**

1. **Create a transcript file (manual "fetch").** Ask your agent: **"Create a manual transcript template"** or **"I want to add a manual transcript"**. Say the date, title, with whom, and project (e.g. personal, company). The agent creates a file under `Transcripts/Manual/` with frontmatter and a "# Raw Transcript" section.
2. **Edit the file.** Open the file the agent created, paste or type the transcript under "# Raw Transcript", save.
3. **Summarize.** In Cursor, with that file open or in context, say: **"Summarize this transcript."** The agent creates the meeting note at `Meetings/<Project>/...` using the summarize skill.
4. **Review** the meeting note (especially speaker attribution—HiNotes has no labels).
5. Say: **"Distill this meeting note."** The agent updates People/Memory/Metadata and fills the note's # Distilled section.

Manual transcripts always need **review before distill**; Fireflies can be processed straight through.

---

## Where things live

- **Transcripts** – Raw input: `Transcripts/Fireflies/<account>/`, `Transcripts/Manual/`. Project is in transcript frontmatter only (not in folder path).
- **Meetings** – Summarized notes: `Meetings/<Project>/` (includes Context, Atmosphere, Summary, Decisions, Action Items, Unresolved Points, Signals, Self-evaluation).
- **People** – Per-person memory: `People/<Project>/<PersonName>.md`.
- **Memory** – Product, Org, Decisions, Personal: `Memory/<Project>/Product/<topic>.md`, `Memory/<Project>/Org/<topic>.md`, `Memory/<Project>/Decisions/decisions.md`, `Memory/<Project>/Personal/self_evaluation.md`.
- **Metadata** – e.g. user name: `Metadata/User.md`.
- **Scripts** – Stable CLI/ingestion only: `scripts/`.
- **Temporal** – One-off scripts, logs, scratch: **`.tmp/`** only. Do not put temporal files in your knowledge base or in `scripts/`.

---

## How the agent runs things

Your **agent** runs deterministic steps via the repo's scripts (e.g. `python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>` for fetch). Init, fetch, summarize, and distill are exposed through **skills** so the agent can run them when you ask—no need for you to type commands. If the repo includes a `lexicon` script, the agent can call that from the repo root; otherwise it calls the Python scripts directly.

---

## Skills

Lexicon ships **skills** in `.cursor/skills/` so your agent can run init, fetch, summarize, and distill:

- **lexicon-process** – "Process my Fireflies meetings for [date] on my [account] account" → fetch, then summarize each transcript into a meeting note, then distill each note into People/Memory/Metadata.
- **lexicon-manual-template** – "Create a manual transcript template" or "I want to add a manual transcript" → create a stub file under `Transcripts/Manual/` (user edits it, then asks to summarize).
- **lexicon-summarize** – "Summarize this transcript" → create a meeting note at `Meetings/<Project>/` from the current or selected transcript (includes Context, Atmosphere, Summary, Decisions, Action Items, Unresolved Points, Signals, Self-evaluation; uses summarize rule).
- **lexicon-distill** – "Distill this meeting note" → update People/Memory/Metadata from the current or selected note and fill its **# Distilled** section (uses distill rule).

You can **edit** these skills in `.cursor/skills/<name>/SKILL.md` to match how you want summaries and distillation to work.

---

## Docs

This repo includes:
- **Scripts** (`scripts/`) – Python scripts for fetching and ingesting transcripts
- **Rules** (`.cursor/rules/`) – Cursor rules for summarizing and distilling meeting notes
- **Skills** (`.cursor/skills/`) – Cursor skills for agent-driven automation
- **Templates** (`.cursor/templates/`) – Meeting note template

See the code and inline documentation for details. You can customize the rules and skills to match your workflow.

---

## License and contributions

This project is licensed under the **MIT License**. See [LICENSE](LICENSE).

You may use, copy, modify, and distribute the software under the terms of that license. The software is provided **as is**, without warranty of any kind; the authors and copyright holders have no liability for any use of this tool or the data you process with it.
