---
name: lexicon-triage
description: Interactive triage — recap with user, update Memory current truth, clean Ideas queue. Not for meetings. Use when user says "triage <project>", "recap <project>", or wants to discuss how things are going and update memory.
---

# Triage a project

Interactive session: **recap → discuss → update Memory → clean Ideas**. Meetings are read-only context.

**Rule:** `.cursor/rules/triage.mdc`  
**Charter:** `Memory/Lexicon/processing-strategy.md`

## What triage is / is not

| Yes | No |
|-----|-----|
| Conversation: what happened, how you're doing, open problems | Processing or editing meeting notes |
| Update `# Current model` (area layout) or durable sections (topic layout), resolve open decisions | Distilling meetings (use **lexicon-distill**) |
| Refresh People `# Current read` | Appending `# Evidence` from meetings |
| Promote / Retire / Keep **Ideas** and **Clippings** | Setting `triaged` on `Meetings/` |

**Ideas disposition (user rule):** **Keep** only if you will **keep editing** the idea file. Otherwise **Promote** knowledge into Memory (then delete the idea) or **Retire** if stale.

**Distill** writes important statements to `# Evidence`. **Triage** synthesizes into `# Current model` (or `# What we learned` on topic-slug projects) when you agree.

## Inputs

- **project** — required (e.g. `personal`, `acme`)
- **period** — optional. If missing, suggest since last triage or last ~2 weeks — do not default to all-time.

## Optional: Plan mode (visible steps)

For a **large** triage (memory + many ideas), start in **Plan mode** so phases are explicit before bulk file ops:

| Phase | What happens |
|-------|----------------|
| 1. Queue | Run `triage_queue.py`; read recap + pending decisions + meetings context |
| 2. Recap | Conversation — narrative, mental state, corrections (**no writes**) |
| 3. Memory | Propose updates; user approves |
| 4. Ideas | Cluster queue → Promote / Keep / **Retire (delete)**; user approves |
| 5. Log | Append `Metadata/recap/<project>/YYYY-MM.md` |

Switch to **Agent mode** to execute approved writes. Small sessions can stay in Agent throughout.

## Steps

1. **Queue** — Run:
   ```bash
   python3 scripts/triage_queue.py --project <project> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
   ```
   Read: previous triage, pending decisions, **recent meetings (context)**, **ideas queue**.

2. **Recap (conversation)** — Narrative from recent meetings + Memory + Me.md (if present). Discuss open problems. Wait for user input before writes.

3. **Memory updates** — Propose changes, resolve open decisions, rare Direction edits, People `# Current read`. User approves first.

4. **Ideas queue** — Propose Promote / Keep / Skip / Retire per idea (cluster when possible). User approves first.

5. **Log** — Append to `Metadata/recap/<project>/YYYY-MM.md`.

6. **Report** — What changed in Memory, ideas processed, what remains in queue.

## Error handling

- **Unknown project** — List `Meetings/*/` and `Ideas/*/`; ask user to pick.
- **Empty ideas queue** — OK; triage can still be recap + memory-only.
- **No recap yet** — First triage; note that in opening.

## Do not

- Edit meeting files or set `triaged` on meetings.
- Update `# Current model` or durable synthesis sections without user approval.
- Append meeting evidence during triage (that's distill).
- Process hundreds of ideas in one session without clustering.
