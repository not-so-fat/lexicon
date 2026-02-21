# Lexicon

**AI-ready organizational memory from meeting transcripts.**

Your Cursor agent turns transcripts (Fireflies, manual, or pasted) into structured Markdown: meeting notes → People, Product, and Org memory. So you can query naturally: "What did we agree with Sarah?" No new app, no extra LLM API—your agent runs this repo's scripts and skills when you ask.

---

## Quick start

1. **Clone** this repo.
2. **Configure** – Copy `.env.example` to `.env`. Minimum setup is a few variables:
   - **LEXICON_USER_NAME** – Your name (for AI Evaluation in meeting notes).
   - For Fireflies, one account is enough to start. Use the suffix **personal** (default), e.g.:
     ```bash
     LEXICON_USER_NAME=Thomas A. Anderson
     FIREFLIES_API_KEY_personal=ff_...
     EMAIL_personal=you@example.com
     PROJECT_personal=personal
     ```
   You can add more Fireflies accounts with a different suffix (e.g. `_acme`, `_work`): add `FIREFLIES_API_KEY_<suffix>`, `EMAIL_<suffix>`, and optionally `PROJECT_<suffix>` so notes go to the right project.  
   Then run `pip install -r requirements.txt`.
3. **Fireflies** – Ask: *"Process my Fireflies meetings for today on my personal account."* Agent runs fetch → summarize → distill. Transcripts in `Transcripts/Fireflies/<account>/`, notes in `Meetings/<Project>/`, memory updated.
4. **Manual** – Ask: *"Create a manual transcript template."* Give date, title, with whom, project. Agent creates a file in `Transcripts/Manual/`; you paste the transcript, then say *"Summarize this transcript"* and (after review) *"Distill this meeting note."*

---

## What it does

- **Fetch** – Fireflies by date/account, or manual template (you edit, then summarize).
- **Summarize** – Raw transcript → structured meeting note (Context, Summary, Decisions, Action Items, Unresolved Points, Signals, AI Evaluation).
- **Distill** – Meeting note → durable memory in `People/<Project>/`, `Memory/<Project>/` (product, org, decisions, personal).

Philosophy: prefer recall over compression; notes are evidence. Early-stage signals matter—preserve them.

---

## Where things live

| What | Path |
|------|------|
| Transcripts | `Transcripts/Fireflies/<account>/`, `Transcripts/Manual/` (project in frontmatter) |
| Meeting notes | `Meetings/<Project>/` |
| People / Memory | `People/<Project>/`, `Memory/<Project>/` (Product, Org, Decisions, Personal) |
| Scratch / logs | **`.tmp/`** only |

---

## Skills (what you say)

| Say | Skill does |
|-----|------------|
| "Process my Fireflies meetings for [date] on my [account] account" | Fetch → summarize each → distill each |
| "Create a manual transcript template" | Stub file in `Transcripts/Manual/`; you paste, then summarize |
| "Summarize this transcript" | Meeting note at `Meetings/<Project>/` |
| "Distill this meeting note" | Update People/Memory/Metadata, fill # Distilled |

Edit skills in `.cursor/skills/<name>/SKILL.md`. Rules in `.cursor/rules/` (summarize, distill).

---

## License

MIT. See [LICENSE](LICENSE). Software provided as is; no warranty or liability.
