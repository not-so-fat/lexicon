---
name: lexicon-review
description: Weekly cross-area objectives review — re-anchor on objectives, read evidence, propose status, retire what's done or missed. Global, not per-project. Use when the user says "review objectives", "weekly review", or asks how they're doing against their goals.
---

# Review objectives

Interactive weekly session: **re-anchor → evidence → status → retire → route → log**.
Global across all areas. Memory and meeting notes are read-only here.

**Rule:** `.cursor/rules/review.mdc`
**Reference:** `docs/OBJECTIVES.md`

## What review is / is not

| Yes | No |
|-----|-----|
| Read `Objectives.md` and `Direction/<area>.md` | Editing `Memory/`, `People/` or meeting notes |
| Propose `moving` / `stalled` / `drifting` per objective | Producing a numeric score of any kind |
| Retire objectives; append to `Objectives.evidence.md` | Opening an objective without `Done when` and `Obstacle` |
| Edit `Direction/<area>.md` when a principle or standard changes | Triaging the Ideas queue (use **lexicon-triage**) |

**Hard boundary:** review never writes `Memory/`. Triage never writes `Objectives.md` or `Direction/`.

## Steps

1. **Queue** — run:
   ```bash
   python3 scripts/review_queue.py
   ```
   Read: cap and WIG state, per-objective horizon and evidence staleness, past-horizon list, areas with no objective.

2. **Re-anchor** — for each objective, restate the outcome **and its obstacle** before reading any evidence. Ordering matters: naming the expected failure first means the evidence gets read against it rather than for confirmation.

3. **Evidence** — for each objective, report what happened since the last review, reading **only** the paths in its `Evidence:` field. State what you found. Do not judge yet.

4. **Status** — propose one of `moving` / `stalled` / `drifting` per objective. Where you propose `drifting`, name which mechanism it resembles:

   | Mechanism | Looks like |
   |---|---|
   | Context exhaustion | the week filled; the original intent faded |
   | Pattern-matching override | reactive work won over the stated objective |
   | Inherited drift | absorbed someone else's priorities |
   | Value conflict | the objective opposes something held more strongly |
   | Subgoal displacement | an intermediate goal is being optimized at the parent's expense |

   **Wait for the user.** They accept or edit. The verdict is theirs — an agent assessing whether a week served its objectives fails in the same directions as the agent that helped run the week.

5. **Retire** — objectives that are achieved or past horizon leave `## Active`, and one dated line per retirement is appended to `Objectives.evidence.md`:
   ```markdown
   - YYYY-MM-DD — <title> — **Outcome:** achieved | missed | withdrawn — <one line> — Area: <area>, opened YYYY-MM-DD
   ```
   **At cap, no new objective opens without either a retirement or an explicit reaffirmation of all current ones.** Say this out loud when the user proposes a new objective at cap.

   Before ending the session, stamp `Objectives.md`'s frontmatter with today's date: `reviewed:` always (the file was read end-to-end this session regardless of whether anything changed), and `objectives_updated:` only if `## Active` actually changed (a retirement or a new objective).

6. **Route** — anything that turned out not to be an objective goes where it belongs:
   - No finish line, can't be failed → `## Principles` in `Direction/<area>.md`
   - No finish line, has a quality bar → `## Standards` in `Direction/<area>.md`
   - Has a deliverable → it's a project; it leaves the vault (Linear, repo, task list)

7. **Log** — append to `Metadata/review/YYYY-Www.md` (ISO week). Record: status per objective, retirements with outcomes, what was routed out, and the WIG for the coming week.

8. **Verify** — run:
   ```bash
   python3 scripts/lint_vault.py
   ```
   Do not end the session on a non-zero exit. A sixth objective, two WIGs, a missing `Obstacle:`, or a disallowed `Direction/<area>.md` section is exactly what this ritual exists to prevent, and none of it is enforced until this runs — fix what it flags before reporting.

9. **Report** — what changed, what was retired, what remains, the named WIG, and the lint result from step 8.

## Error handling

- **No `Objectives.md`** — offer to scaffold it (`python3 scripts/lexicon_init.py`), then run the session as a first authoring pass.
- **Cap breached on entry** — surface it before anything else; the session's first job is getting back under the cap.
- **Area with no objectives** — normal. An area governed only by Standards for a cycle is correct, not a gap. Say so rather than proposing one to fill the hole.
- **No evidence found for an objective** — report it plainly. Absence of evidence is itself the strongest drift-by-omission signal.

## Do not

- Produce a score, a percentage, or a rating.
- Write to `Memory/`, `People/` or meeting notes.
- Open an objective missing `Done when` or `Obstacle`.
- Open a sixth objective. Retire first.
- End the session on a non-zero `lint_vault.py` exit (step 8).
- Treat a `Done when` as a metric — it is a recognition condition.
