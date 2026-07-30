#!/usr/bin/env python3
"""
Create Lexicon folder skeleton if missing. Sync primary user from .env to Metadata/User.md. Remind to set .env.

Usage: python scripts/lexicon_init.py

Run from repo root. Safe to run multiple times.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")

DIRS = [
    "Sources",
    "Sources/Transcripts",
    "Sources/Transcripts/Fireflies",
    "Sources/Transcripts/HiDock",
    "Sources/Transcripts/Manual",
    "Sources/Meetings",
    "Sources/Ideas",
    "Sources/Clippings",
    "Evidence",
    "Synthesis",
    "Direction",
    "Direction/Lenses",
    "Metadata",
    "Metadata/review",
    "Metadata/usage",
]

DIRECTION_TEMPLATE = """---
area: {area}
direction_updated: 
---

# Direction — {title}

*Constant-input tier. What the evidence says → `Synthesis/{area}.md`; the dated
facts → `Evidence/{area}/`. Horizon-bound intentions → `Objectives.md`.*

## Purpose

<Why this area exists. Rarely changes.>

## Principles

<Standing constraints. Cannot be failed.>

## Standards

<What "well-maintained" means here. No finish line, but a quality bar.>
"""

OBJECTIVES_TEMPLATE = """\
---
cycle: 
objectives_updated: 
reviewed: 
---

# Objectives

*Intentions only. Max 5 active across **all** areas; exactly one marked `[WIG]`.
Human-approved — no agent writes here outside a review session.
What the evidence says → `Synthesis/`. Standing constraints → `Direction/<area>.md`.*

**Membership test**

> No finish line, can't be failed → **Principle** (`Direction/<area>.md`)
> No finish line, but has a quality bar → **Standard** (`Direction/<area>.md`)
> Has a date and can be missed → **Objective** (here)
> Has a deliverable → it's a **Project** — it does not live in this vault
> Runnable procedure, no finish line, too big for one line → **Lens** (`Direction/Lenses/`), pointed at by a Standard

Retiring an objective removes it from `## Active` and appends one dated line to
`Objectives.evidence.md`. There is deliberately no `## Retired` section here:
this file's whole value is staying small enough to read every session.

## Active

<!--
### [WIG] <outcome, not activity>
- **Area:** <area — must match a Direction/<area>.md>
- **By:** YYYY-MM-DD
- **Done when:** <observable recognition condition — not a metric>
- **Obstacle:** <the thing most likely to prevent it>
- **Evidence:** <comma-separated vault paths the review reads>
- **Opened:** YYYY-MM-DD
-->
"""

ENTITY_REGISTRY_TEMPLATE = """\
# Entity registry

Canonical names for people, companies, and products — summarize/distill
normalize transcript mis-hearings against this file.

## Canonical

Human-approved only — agents never add here directly; proposals are approved
in a triage session.

<!--
- **Ada Lovelace** (person) — aliases: Ada Loveless, Ada Lovelance
-->

## Proposed (review at triage)

<!--
- YYYY-MM-DD — **Heard Name** (person?) — likely <new entity | alias of **Canonical**>; heard in [[Sources/Meetings/<area>/<note>]]
-->
"""

OBJECTIVES_EVIDENCE_TEMPLATE = """\
# Retired objectives (append-only)

*One line per retirement. Written only in a review session.*

<!--
- YYYY-MM-DD — <objective title> — **Outcome:** achieved | missed | withdrawn | reclassified — <one line: what actually happened> — Area: <area>, opened YYYY-MM-DD
-->
"""


def _detect_areas(root):
    """User areas: subdirectories of Evidence/ (plus legacy Memory/ pre-migration)."""
    areas = set()
    for tier in ("Evidence", "Memory"):
        tier_dir = os.path.join(root, tier)
        if not os.path.isdir(tier_dir):
            continue
        areas.update(
            name
            for name in os.listdir(tier_dir)
            if name != "Lexicon" and os.path.isdir(os.path.join(tier_dir, name))
        )
    return sorted(areas)


def scaffold_direction(root, areas):
    """One Direction/<area>.md per detected area. Never overwrites."""
    direction_dir = os.path.join(root, "Direction")
    os.makedirs(direction_dir, exist_ok=True)
    created = []
    for area in sorted(areas):
        path = os.path.join(direction_dir, f"{area}.md")
        if os.path.exists(path):
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(DIRECTION_TEMPLATE.format(area=area, title=area.replace("-", " ").title()))
        created.append(path)
    return created


def scaffold_objectives(root):
    """Root Objectives.md + Objectives.evidence.md — the intent tier. Never overwrites."""
    created = []
    for name, template in (
        ("Objectives.md", OBJECTIVES_TEMPLATE),
        ("Objectives.evidence.md", OBJECTIVES_EVIDENCE_TEMPLATE),
    ):
        path = os.path.join(root, name)
        if os.path.exists(path):
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(template)
        created.append(path)
    return created


def _load_env(root):
    env_path = os.path.join(root, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    root = REPO_ROOT
    for d in DIRS:
        path = os.path.join(root, d)
        os.makedirs(path, exist_ok=True)
        print(f"  {path}")
    print("\nFolders OK.")

    areas = _detect_areas(root)
    created = scaffold_direction(root, areas)
    if created:
        print("\nDirection scaffolds created:")
        for path in created:
            print(f"  {path}")

    created = scaffold_objectives(root)
    if created:
        print("\nObjectives scaffolds created:")
        for path in created:
            print(f"  {path}")

    registry = os.path.join(root, "Metadata", "entity_registry.md")
    if not os.path.exists(registry):
        with open(registry, "w", encoding="utf-8") as f:
            f.write(ENTITY_REGISTRY_TEMPLATE)
        print(f"Entity registry scaffold created: {registry}")

    print("Next: python scripts/verify_setup.py")

    _load_env(root)
    user_name = (os.getenv("LEXICON_USER_NAME") or "").strip()
    if user_name:
        metadata_dir = os.path.join(root, "Metadata")
        user_md = os.path.join(metadata_dir, "User.md")
        content = f"Primary user: {user_name}\n"
        with open(user_md, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Synced LEXICON_USER_NAME to {user_md}")

    env = os.path.join(root, ".env")
    if not os.path.isfile(env):
        print("Copy .env.example to .env and set FIREFLIES_API_KEY_<account>, EMAIL_<account>, and optionally LEXICON_USER_NAME.")
        print("HiDock: set HIDOCK_ORGANIZER_ROOT and configure hinotes_organizer output.dir → Sources/Transcripts/HiDock/.")
    else:
        print(".env present.")
        print("  Fireflies: python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>")
        print("  HiDock:    python scripts/hidock_collection.py run  →  python scripts/hidock_pending.py list")


if __name__ == "__main__":
    main()
