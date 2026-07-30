---
name: lexicon-review
description: Use when the user says "review objectives", "weekly review", or asks how they are doing against goals or whether work is still aligned. Global across all areas. Output contract: Objectives.md/Direction/** edits with per-change approval; descriptive tiers stay read-only. Not the per-area triage.
---

# Review objectives

Interactive weekly session: **re-anchor → evidence → status → retire → route → log**.
Global across all areas. Memory and meeting notes are read-only here.

**Rule:** `.cursor/rules/review.mdc`
**Reference:** `docs/OBJECTIVES.md`

## What review is / is not

| Yes | No |
|-----|-----|
| Read `Objectives.md` and `Direction/<area>.md` | Editing `Sources/`, `Evidence/` or `Synthesis/` |
| Propose `moving` / `stalled` / `drifting` per objective | Producing a numeric score of any kind |
| Retire objectives; append to `Objectives.evidence.md` | Opening an objective without `Done when` and `Obstacle` |
| Promote or reject `## Direction candidates` staged by triage in `Synthesis/<area>.md`; promote iterated lens drafts | Producing tier-3 items without provenance (`adopted` date + source) |
| Edit `Direction/<area>.md` when a principle or standard changes | Triaging the Ideas queue (use **lexicon-triage**) |

**Hard boundary:** review never writes `Sources/`, `Evidence/` or `Synthesis/`. Triage never writes `Objectives.md` or `Direction/**`.

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

5. **Retire** — objectives that are achieved, past horizon, or turn out not to belong here at all (see step 6) leave `## Active`, and one dated line per retirement is appended to `Objectives.evidence.md`:
   ```markdown
   - YYYY-MM-DD — <title> — **Outcome:** achieved | missed | withdrawn | reclassified — <one line> — Area: <area>, opened YYYY-MM-DD
   ```
   Use `reclassified` when the item was never an objective — it belongs under a Principle, a Standard, a project tracker, or a task list instead. `withdrawn` stays for the case where it genuinely was an objective and the decision is simply to stop pursuing it. **On a first session, expect most retirements to be `reclassified`, not `achieved` or `missed`** — the membership test in step 6 is what does that sorting, and running it for the first time against an unsorted list is the normal case, not a sign the prior list was wrong.

   **At cap, no new objective opens without either a retirement or an explicit reaffirmation of all current ones.** Say this out loud when the user proposes a new objective at cap.

   Before ending the session, stamp `Objectives.md`'s frontmatter with today's date: `reviewed:` always (the file was read end-to-end this session regardless of whether anything changed), and `objectives_updated:` only if `## Active` actually changed (a retirement or a new objective).

6. **Route** — two flows, both requiring your approval per change:
   - **Out of Objectives:** anything that turned out not to be an objective goes where it belongs, and gets the matching `reclassified` line in `Objectives.evidence.md` from step 5 — routing something out is a retirement, not a silent deletion:
     - No finish line, can't be failed → `## Principles` in `Direction/<area>.md`
     - No finish line, has a quality bar → `## Standards` in `Direction/<area>.md`
     - Runnable procedure, too big for one line → `Direction/Lenses/<name>.md` (promote the iterated draft from `Sources/Ideas/`; a one-line Standard points at it; retire the superseded drafts)
     - Has a deliverable → it's a project; it leaves the vault (Linear, repo, task list)
   - **Into tier 3:** read `## Direction candidates` in each `Synthesis/<area>.md`; promote accepted items as one-line ID'd entries `(adopted YYYY-MM-DD — [[source]])`, reject the rest (tell triage via the review log). Direction files stay under their cap — promoting at cap means retiring another item.

7. **Log** — append to `Metadata/review/YYYY-Www.md` (ISO week). Record: status per objective, retirements with outcomes, what was routed out, and the WIG for the coming week.

8. **Verify** — run:
   ```bash
   python3 scripts/lint_vault.py --json
   ```
   Scope the gate to what this session could have written: fail the session only on an error or warning whose `path` is `Objectives.md`, `Objectives.evidence.md`, or starts with `Direction/`. A vault can carry pre-existing lint debt — evidence-log or frontmatter hygiene issues that predate this session and have nothing to do with it — and a gate that blocks on that debt would block every review forever, which in practice means the gate gets ignored, which is worse than not having it. Fix what the scoped filter flags (a sixth objective, two WIGs, a missing `Obstacle:`, or a disallowed `Direction/<area>.md` section — exactly what this ritual exists to prevent) before reporting; leave unrelated pre-existing errors for whatever process owns general vault hygiene.

9. **Report** — if `scripts/build_index.py` exists, run it now: files this session wrote are invisible to vault search until the index rebuilds. Not every vault has this script (this engine repo does not) — its absence is a no-op, not an error. Then report: what changed, what was retired, what remains, the named WIG, and the lint result from step 8.

## Error handling

- **No `Objectives.md`** — offer to scaffold it (`python3 scripts/lexicon_init.py`), then run the session as a first authoring pass. A first session also has no `Obstacle` to re-anchor on in step 2 — none exist yet, so they must be authored per objective before evidence is read. Propose a draft from whatever context already exists (a prior schema's rationale field, notes, a conversation) rather than asking cold or inventing one from nothing. Context describing *why* an objective matters (e.g. a `Why now` field) is not an obstacle — an obstacle is the specific thing most likely to make it drift.
- **Cap breached on entry** — surface it before anything else; the session's first job is getting back under the cap.
- **Area with no objectives** — normal. An area governed only by Standards for a cycle is correct, not a gap. Say so rather than proposing one to fill the hole.
- **No evidence found for an objective** — report it plainly. Absence of evidence is itself the strongest drift-by-omission signal.

## Do not

- Produce a score, a percentage, or a rating.
- Write to `Sources/`, `Evidence/` or `Synthesis/`.
- Open an objective missing `Done when` or `Obstacle`.
- Open a sixth objective. Retire first.
- End the session with an unresolved error or warning under `Objectives.md`, `Objectives.evidence.md`, or `Direction/**` (step 8) — pre-existing debt elsewhere does not block the session.
- Treat a `Done when` as a metric — it is a recognition condition.
