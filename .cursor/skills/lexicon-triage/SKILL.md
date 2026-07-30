---
name: lexicon-triage
description: Use when the user says "triage <area>", "recap <area>", or wants to review how an area is going and update its memory. Not for processing meetings or transcripts.
---

# Triage an area

Interactive session: **recap → discuss → rewrite synthesis → clean Ideas**.
Meetings and Evidence are read-only context.

**Rule:** `.cursor/rules/triage.mdc`
**Direction file:** `Direction/Lexicon.md`

## What triage is / is not

| Yes | No |
|-----|-----|
| Conversation: what happened, how you're doing, open problems | Processing or editing meeting notes |
| **Rewrite `Synthesis/<area>.md` wholesale**, stamp `synthesized:` | Distilling meetings (use **lexicon-distill**) |
| Open/update/close `Synthesis/<area>/decisions/<slug>.md` files | Editing `Direction/**` or `Objectives.md` (use **lexicon-review**) |
| Stage `## Direction candidates` for review | Appending evidence, or compacting/deleting it — evidence is permanent |
| Promote / Retire / Keep **Ideas** and **Clippings** | Setting `triaged` on meetings |

**Ideas disposition (user rule):** **Keep** only if you will **keep editing** the
idea file. Otherwise **Promote** (capture in synthesis, then delete the idea) or
**Retire**. Lens drafts stay in Ideas until a review session promotes them.

## Inputs

- **area** — required
- **period** — optional. Default: since the `synthesized:` stamp or last ~2 weeks — never all-time.

## Steps

1. **Queue** — run:
   ```bash
   python3 scripts/triage_queue.py --area <area> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
   ```
   Read: previous triage, **synthesis staleness**, new evidence since the stamp
   (incl. `Pending decision:` bullets), **open decisions + overdue decide-by**,
   recent meetings (context), ideas queue, usage summary.

2. **Recap (conversation)** — narrative from recent meetings + evidence since the
   stamp + previous synthesis. Discuss open problems. **Decision-state conflict
   check:** flag work that contradicts an open decision's acceptance test with no
   dated Veto/Direction/Scope update on file. Wait for user input before writes.

3. **Rewrite synthesis (propose → approve → write)** — rewrite
   `Synthesis/<area>.md` wholesale: `# Current synthesis` (capped narrative,
   cited), `## People` reads, `## Open decisions` index (promote pending bullets,
   open decision files for consequential ones — each needs a `decide-by` and an
   acceptance test), `## Open hypotheses`, `## Direction candidates`. Stamp
   `synthesized: YYYY-MM-DD`. A ⚠ STALE flag or overdue decide-by must not
   survive the session unaddressed — act or explicitly defer with the user.

4. **Entity corrections** — resolve each pending line in
   `Metadata/entity_registry.md` `## Proposed` with the user: approve → move to
   `## Canonical` (entity or alias; optionally fix affected notes/filenames), or
   reject → delete.

5. **Ideas queue** — propose Promote / Keep / Skip / Retire per idea (cluster
   when possible). User approves first. Skip gets no `triaged`; Retire = delete.

6. **Log** — append to `Metadata/recap/<area>/YYYY-MM.md` (recap, synthesis
   changes, decisions touched, entity corrections, ideas, candidates staged,
   carry-forward).

7. **Lint gate** — run:
   ```bash
   python3 scripts/lint_vault.py --files Synthesis/<area>.md <decision files touched> <recap log>
   ```
   Fix errors before finishing.

8. **Report** — synthesis rewritten (what changed), decision files touched,
   entity corrections resolved, ideas processed / remaining, candidates staged
   for the next review, suggested next kick.

## Error handling

- **Unknown area** — list `Sources/Meetings/*/` and `Sources/Ideas/*/`; ask.
- **Empty ideas queue** — OK; triage can be recap + synthesis only.
- **No synthesis file yet** — first triage for the area: create
  `Synthesis/<area>.md` from `.cursor/templates/synthesis_template.md` and say so.

## Do not

- Edit meeting files, append evidence, or delete evidence.
- Rewrite the synthesis without user approval of the proposed content.
- Edit `Direction/**`, `Objectives.md`, `Objectives.evidence.md` — stage
  candidates instead.
- Process hundreds of ideas in one session without clustering.
