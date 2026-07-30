# Objectives

The **normative** tier: what you are trying to make true, by when.

[MEMORY_MODEL.md](MEMORY_MODEL.md) covers what is *true*. This covers what is *intended*.

---

## Why this tier exists

Every tier that came before this one answers **what is true**. Evidence records what
was said; `# Current model` records what we believe now; principles record what has
been committed to. Nothing answered **what am I trying to make true, by when** — a
principle has no date and cannot be missed, and evidence is by definition already
in the past.

The cost of that gap is invisibility, not ignorance. An intention that has quietly
stopped mattering looks exactly like one that is on track, because nothing ever
re-reads it. This tier adds a home for horizon-bound intent (`Objectives.md`) and a
weekly ritual that re-reads it (**review**).

It also removes a conflation. Normative content once sat beside descriptive files
inside the memory tree — so "read the normative tier" was a convention an agent
had to know rather than a path it could follow. The normative tier is now
`Direction/` and `Objectives.md` at the top level; `Sources/`, `Evidence/` and
`Synthesis/` are purely descriptive (see [MEMORY_MODEL.md](MEMORY_MODEL.md)).

---

## The horizon stack

GTD's Horizons of Focus, and where each one lives here:

| Horizon | Question | Home |
|---|---|---|
| **H5** — Purpose & principles | why this exists; what can never be traded away | `Direction/<area>.md` — `## Purpose`, `## Principles` |
| **H4** — Vision | what it looks like in 3–5 years | no separate home — a vision that earns its keep reads as Purpose |
| **H3** — Goals & objectives | what I'm trying to make true this cycle | `Objectives.md` (root, all areas) |
| **H2** — Areas of responsibility | the hats worn continuously | the area directories; the bar is `## Standards` |
| **H1** — Projects | outcomes with a finish line | **not in this vault** — Linear, repos, task lists |
| **Runway** — Next actions | the next physical action | **not in this vault** |

H1 and runway are excluded deliberately. Admitting them is how a normative tier
degrades into a task list: a project has a deliverable, a deliverable generates
status, and the file that was meant to hold five intentions ends up holding forty
tasks. Work with a finish line belongs where the work happens.

---

## `area:` is H2

The frontmatter `area:` field (`personal`, `acme`, …) does not name H1 projects. (It was called `project:` before this rename; the old key still works — see UPDATING.md.)
Those values are **Areas of Responsibility** — ongoing hats with no finish line. So
H2 needs no new structure: it is already the `<area>` directory layout under
`Sources/`, `Evidence/` and `Synthesis/`.

Throughout these docs, **area** is the value of the `area:` frontmatter key. The key is *not*
renamed — the churn across every existing note is not worth the terminology gain.

---

## The membership test

Verbatim from `Objectives.md`, where the wrong thing actually gets added:

> No finish line, can't be failed → **Principle** (`Direction/<area>.md`)
> No finish line, but has a quality bar → **Standard** (`Direction/<area>.md`)
> Has a date and can be missed → **Objective** (here)
> Has a deliverable → it's a **Project** — it does not live in this vault
> Runnable procedure, no finish line, too big for one line → **Lens** (`Direction/Lenses/`), pointed at by a Standard

The test appears **only** there — it is not copied into each `Direction/<area>.md`.
`Objectives.md` is the point of decision, so the test sits at that point, once.

---

## The cap

**Max 5 active objectives across all areas** — not 5 per area.

Per-area is the version that fails. The failure mode is accumulation: each cycle
adds objectives without retiring the last ones, producing *"fifteen active goals
and zero genuine focus within three cycles."* A cap of 5 per area across three
areas **is** 15 — the failure number exactly, reached while every area still looks
disciplined on its own.

That is also why all objectives live in one file rather than one per area. A cap
enforced by a script is a number you can argue with; a cap enforced by a file
boundary means adding a sixth puts the other five on screen, and the question
becomes which one to retire. The same constraint serves the file's second job: it
must stay small enough to read at the start of **every** session — roughly forty
lines. Three areas' worth of separate objective files can never be read that often.
One page can.

Objectives are listed flat, with `**Area:**` as a field rather than grouped under
area headings. Grouping would spread five items across three headings and cost
exactly the visibility the file exists to provide.

Cap default is 5; override with `LEXICON_OBJECTIVE_CAP`. `lint_vault.py` errors
above it.

---

## The objective schema

The heading is the outcome, not the activity. Six fields, all required —
`lint_vault.py` errors on a missing one.

```markdown
### [WIG] <outcome, not activity>
- **Area:** <area — must match a Direction/<area>.md>
- **By:** YYYY-MM-DD
- **Done when:** <observable recognition condition — not a metric>
- **Obstacle:** <the thing most likely to prevent it>
- **Evidence:** <comma-separated vault paths the review reads>
- **Opened:** YYYY-MM-DD
```

| Field | Why |
|---|---|
| **Area** | Ties the objective to a `Direction/<area>.md`, so it is answerable to a stated purpose rather than free-floating. |
| **By** | The date it can be missed by — the one property that makes this an objective and not a standard. |
| **Done when** | A recognition condition, not a metric: a state you could point at on sight. A number would become the thing served, and the objective would get hit while the intent behind it did not. |
| **Obstacle** | The V2MOM borrow. For a failure mode that is specifically drift, naming the expected cause of drift *in advance* is the highest-value line on the card. |
| **Evidence** | The vault paths review reads for this objective — and only these. Keeps the weekly read bounded, and turns "nothing found" into a finding rather than a failed search. |
| **Opened** | Ages the objective, so one that has been carried for three cycles is visible as such at retirement. |

`Evidence:` paths are files or directories, human-maintained — typically under
`Evidence/<area>/…` or `Synthesis/<area>…`. Every path **must exist on disk**:
a dead path makes the review's evidence step silently empty, so `lint_vault.py`
errors on it. "Newest evidence" means the newest dated bullet in a file, or the
newest dated file in a directory — nothing else in the vault changes shape to
support this.

---

## Frontmatter

`Objectives.md` carries three frontmatter fields, none of them read by
`parse_objectives` — they describe the file, not an objective:

```yaml
---
cycle:
objectives_updated:
reviewed:
---
```

| Field | Meaning | Stamped by |
|---|---|---|
| **cycle** | The cycle label (e.g. `2026-Q3`) all objectives in this file are bound to. | Set by hand when a new cycle starts. |
| **objectives_updated** | The date `## Active` last actually changed — a retirement or a new objective. | The review skill, step 5, only when `## Active` changes. |
| **reviewed** | The date of the last full review session, whether or not anything changed. | The review skill, step 5, every session. |

`reviewed:` is a fallback signal, not the primary one: `review_queue.py` also
reads the newest `Metadata/review/YYYY-Www.md` file and takes the later of the
two, so a session that forgets to log the week file still moves "days since
review" forward.

---

## The WIG

Exactly one objective carries the `[WIG]` prefix — the Wildly Important Goal. Once
at least one objective exists, zero or two `[WIG]`s is a lint error, not a
warning: the discipline is only real when the choice is forced. (An empty
`## Active` — the shipped scaffold — has no objective to attach a WIG to, so
`lint_objectives` returns clean rather than errors on zero.) 4DX's premise is
that naming *one* changes what the week actually does; five equal priorities
are none.

The cap and the WIG are the **entire** 4DX borrow. No lead and lag measures, no
scoreboard, no cadence of accountability.

---

## Framework discipline

| Framework | Borrowed | Not borrowed |
|---|---|---|
| **GTD Horizons** | Primary — the taxonomy H5 → runway, and the weekly review cadence | The full runway/next-action machinery |
| **4DX** | The cap and the single WIG | Lead/lag measures, scoreboards, accountability cadence |
| **V2MOM** | The `Obstacle` line | Vision, values, methods, measures |

One primary framework, by design. Running two taxonomies at once means every item
has two plausible homes and neither is authoritative, which is the state this tier
was built to end.

Most goal frameworks need **18–24 months** to take root. A quarter in, "this isn't
working" is far more likely to be the ordinary discomfort of the practice than
evidence against it. Fix the practice — the objectives, the retirements, the
weekly slot. Don't swap the framework.

---

## The weekly ritual

Global, cross-area, weekly. Say *"review my objectives"*.
Skill: `.cursor/skills/lexicon-review/SKILL.md`. Rule: `.cursor/rules/review.mdc`.

| Step | What happens | Writes |
|---|---|---|
| 1. Queue | `python3 scripts/review_queue.py` — cap, WIG, horizons, evidence staleness | none |
| 2. Re-anchor | Agent restates each objective **and its obstacle**, before reading any evidence | none |
| 3. Evidence | Per objective: what happened since the last review, from its `Evidence:` paths only | none |
| 4. Status | Agent proposes `moving` / `stalled` / `drifting`; you accept or edit | none |
| 5. Retire | Achieved, past-horizon, or reclassified objectives leave `## Active` with an outcome line; frontmatter `reviewed:` (and `objectives_updated:` if `## Active` changed) gets stamped | `Objectives.md`, `Objectives.evidence.md` |
| 6. Route | What turned out to be a standard, a lens, or a project leaves for its real home; `## Direction candidates` staged by triage are promoted or rejected | `Direction/<area>.md`, `Direction/Lenses/`, `Objectives.evidence.md` |
| 7. Log | Append the session | `Metadata/review/YYYY-Www.md` |
| 8. Verify | `python3 scripts/lint_vault.py --json`, scoped to errors/warnings under `Objectives.md`, `Objectives.evidence.md`, or `Direction/**` — pre-existing debt elsewhere does not block the session | none |
| 9. Report | What changed, what was retired, what remains, the named WIG, and the lint result | none |

Two orderings are load-bearing:

- **Obstacle before evidence** (2 before 3) — evidence read after the expected
  failure is read *against* it, not for confirmation.
- **Retire before open** (5 before any new objective) — see Retirement below.

Review is global and weekly; **triage** is per-area and runs when material has
accumulated. A per-area session structurally cannot enforce a global cap or name
one WIG across areas. The two loops share evidence and nothing else:

- Triage never writes `Objectives.md`, `Objectives.evidence.md` or `Direction/**` —
  it stages `## Direction candidates` in `Synthesis/<area>.md` for review to read.
- Review never writes `Sources/`, `Evidence/` or `Synthesis/`.

An area with zero active objectives is **not** a gap. An area governed only by its
Standards for a cycle is correct, and the queue labels it that way.

---

## Why there is no score

There is no numeric alignment score anywhere in this system, and adding one would
be a regression. Goodhart's Law: a measurable proxy for alignment becomes the thing
served, so the week gets optimized to move the number rather than the objective.
And correlated uncertainty: an agent judging whether your week served your
objectives fails in the same directions as the agent that helped you run that week,
so the verdict is least trustworthy exactly where you would lean on it hardest.

The division of labour follows and is not negotiable: **the agent gathers evidence
and proposes; the human judges.** The vocabulary is exactly three words —
`moving`, `stalled`, `drifting` — chosen because they do not compress into a
metric and so cannot be optimized against. Where the agent proposes `drifting` it
also names which mechanism the drift resembles: context exhaustion,
pattern-matching override, inherited drift, value conflict, or subgoal
displacement. You accept or edit. This is the same propose-then-approve pattern
every Memory write already uses.

---

## Retirement

Retirement, not authoring, is the binding constraint. Opening an objective is easy
and closing one never survives contact with practice, so closing is made to produce
something:

- The objective leaves `## Active` in `Objectives.md`.
- One dated line is appended to `Objectives.evidence.md`: outcome `achieved` /
  `missed` / `withdrawn` / `reclassified`, one line on what actually happened,
  the area, and the date it was opened.

`missed`, `withdrawn`, and `reclassified` are first-class outcomes, not a euphemism
for "deleted." `withdrawn` is for a genuine objective the decision is to stop
pursuing. `reclassified` is for an item that was never an objective at all — the
membership test says it has no finish line (a Principle or a Standard) or has a
deliverable (a project) — and Route (step 6 of the ritual) sends it to where it
belongs while this step logs the line. On a first review, expect most retirements
to be `reclassified`: sorting a previously unsorted list into the membership
test's four buckets is the normal outcome of running the test for the first time,
not a sign the prior list was wrong. An objective missed and recorded honestly is
worth more to the next cycle than one quietly deleted.

There is deliberately **no `## Retired` section** in `Objectives.md`. A retained
section grows without bound inside the one file whose whole value is staying small
enough to read every session; the log is a sibling file for the same reason
evidence is a sibling of the current model.

**Retire before open.** At cap, no new objective opens without either a retirement
or an explicit reaffirmation of all five. That rule is where the constraint is
actually enforced — everything else about the cap is arithmetic.

---

## What this cannot see

**Drift by commission — the ratio of goal-aligned investment to the time actually
available — is not computable from this vault**, because the vault never observes
where hours went. It sees meetings that happened, evidence bullets someone wrote,
and recap logs. From those it can tell you that an objective has had nothing under
its `Evidence:` paths for three weeks. It cannot tell you that you spent those
three weeks on something else.

So review is good at **drift by omission** — the required action not taken after a
phase completed — and blind to **drift by commission**. Read a clean review as
"nothing I track has stalled", not as "my time was well spent."

Closing that gap needs a time source this vault does not have. It should be
designed as one, rather than approximated by smuggling a task list into the
normative tier.

---

See also: [MEMORY_MODEL.md](MEMORY_MODEL.md), `Direction/README.md`, `Objectives.md`.
