# Direction

The **normative** tier: what each area is for and what "well-maintained" means
there. One file per area, mirroring the area directories under `Memory/`.

| Section | Horizon | Test |
|---|---|---|
| `## Purpose` | H5 | Why this area exists. Rarely changes. |
| `## Principles` | H5 | Standing constraints. Cannot be failed — they are not targets. |
| `## Standards` | H2 | What "well-maintained" means. No finish line, but a quality bar. |

No other `##` sections are permitted — `lint_vault.py` enforces this.

Horizon-bound intentions (H3) live in the root `Objectives.md`, not here, so
that the cap across all areas stays visible in one place. Projects (H1) and
next actions do not live in this vault at all — admitting them is how this
tier degrades into a task list.

`Memory/` is the **descriptive** tier: what is true. This directory is what you
intend to make true.
