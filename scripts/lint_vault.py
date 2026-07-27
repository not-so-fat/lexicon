#!/usr/bin/env python3
"""
Lint vault frontmatter and evidence hygiene.

Checks (agents and humans both drift — this keeps the maps trustworthy):
  1. Meetings/Ideas/Clippings notes have YAML frontmatter and a date
     (`date:`/`created:`/`published:` or a YYYY-MM-DD filename prefix).
  2. Evidence bullets (in `*.evidence.md` and legacy inline `# Evidence`
     sections) start with `- YYYY-MM-DD —` and stay one line / short
     (~30 words; hard limit MAX_BULLET_CHARS).
  3. Area model files with evidence have a `model_updated:` frontmatter date
     (or legacy `# Current model (last updated: ...)` heading).
  4. Legacy inline `# Evidence` sections are flagged for migration to the
     sibling `<Area>.evidence.md`.

Errors exit 1 (missing frontmatter/dates, oversized bullets); warnings exit 0.

Usage:
  python3 scripts/lint_vault.py [--project <project>] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import date

from review_queue import objective_cap, parse_objectives, unfenced_lines

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
DATED_BULLET_RE = re.compile(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s*[—-]")
BULLET_RE = re.compile(r"^\s*-\s+\S")
MODEL_HEADING_DATE_RE = re.compile(
    r"^#\s*Current model\s*\(last updated:\s*\d{4}-\d{2}-\d{2}\)", re.IGNORECASE | re.MULTILINE
)

MAX_BULLET_CHARS = 240  # ~30 words; detail belongs in the linked meeting note

CAPTURE_ROOTS = ("Meetings", "Ideas", "Clippings")
SKIP_NAMES = {"readme.md", "index.md"}
MODEL_SKIP = {"readme.md", "index.md", "direction.md"}

DIRECTION_ALLOWED_SECTIONS = ("purpose", "principles", "standards")
LEGACY_LEXICON_CHARTER = "Memory/Lexicon/processing-strategy.md"
OBJECTIVE_FIELD_LABELS = {
    "area": "Area",
    "by": "By",
    "done when": "Done when",
    "obstacle": "Obstacle",
    "evidence": "Evidence",
    "opened": "Opened",
}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def frontmatter_block(text: str) -> str | None:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else None


def has_date(fm_block: str | None, fname: str) -> bool:
    if FILENAME_DATE_RE.match(fname):
        return True
    if not fm_block:
        return False
    return bool(re.search(r"^(date|created|published):\s*\S", fm_block, re.MULTILINE))


def lint_capture_files(project: str | None) -> list[dict]:
    issues: list[dict] = []
    for root_name in CAPTURE_ROOTS:
        base = REPO_ROOT / root_name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.lower() in SKIP_NAMES or path.name.startswith("."):
                continue
            rel = path.relative_to(REPO_ROOT)
            if project and len(rel.parts) > 2 and rel.parts[1].lower() != project.lower():
                continue
            text = read(path)
            fm = frontmatter_block(text)
            if fm is None:
                issues.append(
                    {"level": "error", "path": str(rel), "issue": "missing YAML frontmatter"}
                )
            if fm and re.search(r"^project:\s*\S", fm, re.MULTILINE) and not re.search(
                r"^area:\s*\S", fm, re.MULTILINE
            ):
                issues.append(
                    {
                        "level": "warning",
                        "path": str(rel),
                        "issue": "legacy `project:` key — run scripts/migrate_area_key.py to rewrite as `area:`",
                    }
                )
            if not has_date(fm, path.name):
                issues.append(
                    {
                        "level": "error",
                        "path": str(rel),
                        "issue": "no date (frontmatter date/created or YYYY-MM-DD filename prefix)",
                    }
                )
    return issues


def lint_bullet_lines(lines: list[tuple[int, str]], rel: str) -> list[dict]:
    issues: list[dict] = []
    for lineno, ln in lines:
        if not BULLET_RE.match(ln):
            continue
        if not DATED_BULLET_RE.match(ln):
            issues.append(
                {
                    "level": "error",
                    "path": rel,
                    "issue": f"line {lineno}: evidence bullet not dated (`- YYYY-MM-DD — ...`)",
                }
            )
        if len(ln.strip()) > MAX_BULLET_CHARS:
            issues.append(
                {
                    "level": "error",
                    "path": rel,
                    "issue": (
                        f"line {lineno}: evidence bullet {len(ln.strip())} chars "
                        f"(max {MAX_BULLET_CHARS}, ~30 words) — detail belongs in the meeting note"
                    ),
                }
            )
    return issues


def inline_evidence_lines(text: str) -> list[tuple[int, str]]:
    """Bullet lines inside a legacy inline `# Evidence` section."""
    out: list[tuple[int, str]] = []
    in_section = False
    for i, ln in enumerate(text.splitlines(), 1):
        stripped = ln.strip().lower()
        if stripped.startswith("# evidence"):
            in_section = True
            continue
        if in_section and ln.startswith("# "):
            in_section = False
            continue
        if in_section:
            out.append((i, ln))
    return out


def lint_memory(project: str | None) -> list[dict]:
    issues: list[dict] = []
    memory = REPO_ROOT / "Memory"
    if not memory.is_dir():
        return issues
    projects = (
        [memory / project]
        if project
        else [p for p in sorted(memory.iterdir()) if p.is_dir() and p.name != "Lexicon"]
    )
    for proj_dir in projects:
        if not proj_dir.is_dir():
            continue
        for path in sorted(proj_dir.rglob("*.md")):
            rel_parts = path.relative_to(proj_dir).parts
            if "_legacy" in rel_parts or path.name.lower() in SKIP_NAMES:
                continue
            rel = str(path.relative_to(REPO_ROOT))
            text = read(path)

            if path.name.endswith(".evidence.md"):
                lines = list(enumerate(text.splitlines(), 1))
                issues.extend(lint_bullet_lines(lines, rel))
                continue

            if path.name.lower() in MODEL_SKIP:
                continue

            # Area model file: check date convention + legacy inline evidence.
            inline = inline_evidence_lines(text)
            sibling = path.with_name(path.stem + ".evidence.md")
            has_evidence = bool(inline) or sibling.is_file()
            if inline:
                issues.append(
                    {
                        "level": "warning",
                        "path": rel,
                        "issue": f"inline `# Evidence` (legacy) — migrate to {path.stem}.evidence.md in triage",
                    }
                )
                issues.extend(lint_bullet_lines(inline, rel))
            if has_evidence and "# Current model" in text:
                fm = frontmatter_block(text) or ""
                if not re.search(
                    r"^model_updated:\s*\d{4}-\d{2}-\d{2}", fm, re.MULTILINE
                ) and not MODEL_HEADING_DATE_RE.search(text):
                    issues.append(
                        {
                            "level": "error",
                            "path": rel,
                            "issue": "no `model_updated:` date — staleness tracking needs it (stamp in triage)",
                        }
                    )
    return issues


def lint_objectives() -> list[dict]:
    """Cap, WIG, required fields and horizon hygiene for the global objectives file."""
    issues: list[dict] = []
    path = REPO_ROOT / "Objectives.md"
    if not path.is_file():
        return issues

    objectives = parse_objectives(read(path))
    if not objectives:
        return issues
    cap = objective_cap()
    rel = "Objectives.md"

    if len(objectives) > cap:
        issues.append(
            {
                "level": "error",
                "path": rel,
                "issue": (
                    f"{len(objectives)} active objectives exceeds cap of {cap} — "
                    "retire one before opening another"
                ),
            }
        )

    wigs = sum(1 for obj in objectives if obj["wig"])
    if wigs != 1:
        issues.append(
            {
                "level": "error",
                "path": rel,
                "issue": f"expected exactly one [WIG], found {wigs}",
            }
        )

    areas = set(known_direction_areas())
    today = date.today().isoformat()

    for obj in objectives:
        title = obj["title"]
        for key in obj["missing_fields"]:
            issues.append(
                {
                    "level": "error",
                    "path": rel,
                    "issue": f"`{title}`: missing **{OBJECTIVE_FIELD_LABELS[key]}:**",
                }
            )
        if obj["area"] and areas and obj["area"] not in areas:
            issues.append(
                {
                    "level": "error",
                    "path": rel,
                    "issue": f"`{title}`: area `{obj['area']}` has no Direction/{obj['area']}.md",
                }
            )
        if obj["by"] and obj["by"] < today:
            issues.append(
                {
                    "level": "warning",
                    "path": rel,
                    "issue": (
                        f"`{title}`: past its due date ({obj['by']}) and still active — "
                        "retire it or reopen with a new date in review"
                    ),
                }
            )

    return issues


def known_direction_areas() -> list[str]:
    direction = REPO_ROOT / "Direction"
    if not direction.is_dir():
        return []
    return sorted(
        p.stem for p in direction.glob("*.md") if p.stem.lower() not in ("readme", "index")
    )


def lint_direction() -> list[dict]:
    """Section whitelist, plus migration warnings for the normative tier."""
    issues: list[dict] = []

    direction = REPO_ROOT / "Direction"
    if direction.is_dir():
        for path in sorted(direction.glob("*.md")):
            if path.stem.lower() in ("readme", "index"):
                continue
            rel = str(path.relative_to(REPO_ROOT))
            for line in unfenced_lines(read(path)):
                if not line.startswith("## "):
                    continue
                name = line[3:].strip()
                if name.lower() not in DIRECTION_ALLOWED_SECTIONS:
                    issues.append(
                        {
                            "level": "error",
                            "path": rel,
                            "issue": (
                                f"section `## {name}` not allowed — only Purpose, "
                                "Principles and Standards. Horizon-bound intent "
                                "belongs in Objectives.md"
                            ),
                        }
                    )

    memory = REPO_ROOT / "Memory"
    if not memory.is_dir():
        return issues

    legacy_charter = REPO_ROOT / LEGACY_LEXICON_CHARTER
    if legacy_charter.is_file():
        issues.append(
            {
                "level": "warning",
                "path": LEGACY_LEXICON_CHARTER,
                "issue": (
                    "superseded by Direction/Lexicon.md — `git checkout` does not "
                    "delete files the template removed; `git rm -f` it "
                    "(see docs/UPDATING.md)"
                ),
            }
        )

    areas = set(known_direction_areas())
    for area_dir in sorted(p for p in memory.iterdir() if p.is_dir() and p.name != "Lexicon"):
        legacy = area_dir / "Direction.md"
        if legacy.is_file():
            issues.append(
                {
                    "level": "warning",
                    "path": str(legacy.relative_to(REPO_ROOT)),
                    "issue": (
                        f"un-migrated — move to Direction/{area_dir.name}.md "
                        "and sort into Purpose / Principles / Standards"
                    ),
                }
            )
        elif area_dir.name not in areas:
            issues.append(
                {
                    "level": "warning",
                    "path": str(area_dir.relative_to(REPO_ROOT)),
                    "issue": f"area has no Direction/{area_dir.name}.md",
                }
            )

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint Lexicon vault hygiene")
    parser.add_argument("--project", help="Limit to one project slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    issues = (
        lint_capture_files(args.project)
        + lint_memory(args.project)
        + lint_objectives()
        + lint_direction()
    )
    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warning"]

    if args.json:
        print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
    else:
        if not issues:
            print("Vault clean — no lint issues.")
        for level, items in (("ERROR", errors), ("WARN", warnings)):
            for i in items:
                print(f"{level}  {i['path']} — {i['issue']}")
        if issues:
            print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
