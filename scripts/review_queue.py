#!/usr/bin/env python3
"""
Global objectives review queue — deterministic signals for the weekly review.

Counts, dates and staleness only. This script renders **no judgment**: whether
an objective is moving, stalled or drifting is proposed by the review skill and
decided by the human. See docs/OBJECTIVES.md.

Usage:
  python3 scripts/review_queue.py
  python3 scripts/review_queue.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

from triage_queue import normalize_date, parse_frontmatter

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

DEFAULT_CAP = 5
HORIZON_SOON_DAYS = 14
REVIEW_STALE_DAYS = 14

OBJ_HEADING_RE = re.compile(r"^###\s+(?:(\[WIG\])\s+)?(.+?)\s*$")
FIELD_RE = re.compile(r"^\s*-\s+\*\*(?P<key>[^:*]+):\*\*\s*(?P<val>.*?)\s*$")
DATED_BULLET_RE = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2})")
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
REVIEW_FILE_RE = re.compile(r"^(\d{4})-W(\d{2})\.md$")

REQUIRED_FIELDS = ("area", "horizon", "done when", "obstacle", "evidence", "opened")


def objective_cap() -> int:
    raw = os.environ.get("LEXICON_OBJECTIVE_CAP", "")
    try:
        return int(raw) if raw.strip() else DEFAULT_CAP
    except ValueError:
        return DEFAULT_CAP


def parse_objectives(text: str) -> list[dict]:
    """Objectives under `## Active`. Everything after the next `##` is ignored."""
    objectives: list[dict] = []
    current: dict | None = None
    in_active = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower() == "## active":
            in_active = True
            continue
        if in_active and stripped.startswith("## "):
            break
        if not in_active:
            continue

        heading = OBJ_HEADING_RE.match(line)
        if heading:
            current = {
                "title": heading.group(2).strip(),
                "wig": bool(heading.group(1)),
                "fields": {},
            }
            objectives.append(current)
            continue

        if current is None:
            continue
        field = FIELD_RE.match(line)
        if field:
            current["fields"][field.group("key").strip().lower()] = field.group("val").strip()

    for obj in objectives:
        fields = obj["fields"]
        obj["area"] = fields.get("area", "")
        obj["horizon"] = normalize_date(fields.get("horizon", ""))
        obj["opened"] = normalize_date(fields.get("opened", ""))
        obj["evidence"] = [p.strip() for p in fields.get("evidence", "").split(",") if p.strip()]
        obj["missing_fields"] = [k for k in REQUIRED_FIELDS if not fields.get(k)]
    return objectives


def _newest_dated_bullet(path: Path) -> str:
    newest = ""
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = DATED_BULLET_RE.match(line)
            if match and match.group(1) > newest:
                newest = match.group(1)
    except OSError:
        pass
    return newest


def _newest_dated_filename(directory: Path) -> str:
    newest = ""
    for path in directory.rglob("*.md"):
        match = FILENAME_DATE_RE.match(path.name)
        if match and match.group(1) > newest:
            newest = match.group(1)
    return newest


def newest_evidence_date(root: Path, rel_paths: list[str]) -> str:
    """Newest evidence under the objective's `Evidence:` paths.

    Paths resolve literally — a file yields its newest dated bullet, a
    directory its newest dated filename. Never assumes a naming convention:
    vaults differ on where evidence logs live.
    """
    newest = ""
    for rel in rel_paths:
        target = root / rel
        if target.is_file():
            found = _newest_dated_bullet(target)
        elif target.is_dir():
            found = _newest_dated_filename(target)
        else:
            continue
        if found > newest:
            newest = found
    return newest


def last_review(root: Path) -> tuple[str, str]:
    """(ISO date of the Monday of the newest review week, relpath)."""
    review_dir = root / "Metadata" / "review"
    if not review_dir.is_dir():
        return "", ""
    best_date = ""
    best_path = ""
    for path in sorted(review_dir.glob("*.md")):
        match = REVIEW_FILE_RE.match(path.name)
        if not match:
            continue
        try:
            monday = datetime.strptime(
                f"{match.group(1)}-W{match.group(2)}-1", "%G-W%V-%u"
            ).strftime("%Y-%m-%d")
        except ValueError:
            continue
        if monday > best_date:
            best_date = monday
            best_path = str(path.relative_to(root))
    return best_date, best_path


def known_areas(root: Path) -> list[str]:
    """User areas. `Lexicon` is the tool's own charter, not an area to review."""
    direction = root / "Direction"
    if not direction.is_dir():
        return []
    return sorted(
        path.stem
        for path in direction.glob("*.md")
        if path.stem.lower() not in ("readme", "index", "lexicon")
    )


def _days_between(earlier: str, later: date) -> int | None:
    if not earlier:
        return None
    return (later - date.fromisoformat(earlier)).days


def build_report(root: Path, today: date) -> dict:
    objectives_file = root / "Objectives.md"
    text = (
        objectives_file.read_text(encoding="utf-8", errors="replace")
        if objectives_file.is_file()
        else ""
    )
    frontmatter = parse_frontmatter(text)
    objectives = parse_objectives(text)
    cap = objective_cap()

    for obj in objectives:
        obj["newest_evidence"] = newest_evidence_date(root, obj["evidence"])
        obj["days_since_evidence"] = _days_between(obj["newest_evidence"], today)
        if obj["horizon"]:
            obj["days_to_horizon"] = (date.fromisoformat(obj["horizon"]) - today).days
            obj["past_horizon"] = obj["days_to_horizon"] < 0
        else:
            obj["days_to_horizon"] = None
            obj["past_horizon"] = False
        obj.pop("fields", None)

    areas_with = {obj["area"] for obj in objectives if obj["area"]}
    review_date, review_path = last_review(root)
    reviewed_frontmatter = normalize_date(frontmatter.get("reviewed", ""))
    effective_review = max(review_date, reviewed_frontmatter)
    days_since_review = _days_between(effective_review, today)

    return {
        "cap": cap,
        "active_count": len(objectives),
        "cap_breach": len(objectives) > cap,
        "wig_count": sum(1 for obj in objectives if obj["wig"]),
        "objectives": objectives,
        "horizon_soon": [
            obj["title"]
            for obj in objectives
            if obj["days_to_horizon"] is not None
            and 0 <= obj["days_to_horizon"] <= HORIZON_SOON_DAYS
        ],
        "past_horizon": [obj["title"] for obj in objectives if obj["past_horizon"]],
        "last_review_date": effective_review,
        "last_review_path": review_path,
        "days_since_review": days_since_review,
        "review_stale": days_since_review is None or days_since_review > REVIEW_STALE_DAYS,
        "areas_without_objectives": [a for a in known_areas(root) if a not in areas_with],
    }


def render(report: dict) -> str:
    lines = [
        "# Objectives review queue",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "*Signals only — status is proposed in the review session and decided by you.*",
        "",
        "## Cap and focus",
        "",
    ]

    breach = " ⚠ exceeds cap" if report["cap_breach"] else ""
    lines.append(f"- Active objectives: **{report['active_count']}** / {report['cap']}{breach}")
    if report["wig_count"] == 1:
        lines.append("- WIG: one named")
    elif report["wig_count"] == 0:
        lines.append("- WIG: ⚠ no [WIG] named — 4DX discipline needs exactly one")
    else:
        lines.append(f"- WIG: ⚠ {report['wig_count']} marked [WIG] — expected exactly one")

    if report["last_review_date"]:
        stale = " ⚠ stale" if report["review_stale"] else ""
        lines.append(
            f"- Last review: {report['last_review_date']} "
            f"({report['days_since_review']} days ago){stale}"
        )
    else:
        lines.append("- Last review: none recorded — this is the first review")
    lines.append("")

    lines.extend(["## Objectives", ""])
    if not report["objectives"]:
        lines.append("(none active)")
    for obj in report["objectives"]:
        marker = "[WIG] " if obj["wig"] else ""
        lines.append(f"### {marker}{obj['title']}")
        lines.append(f"- Area: {obj['area'] or '⚠ missing'}")
        if obj["horizon"]:
            if obj["past_horizon"]:
                lines.append(
                    f"- Horizon: {obj['horizon']} ⚠ passed "
                    f"{abs(obj['days_to_horizon'])} days ago — retire or reopen"
                )
            else:
                lines.append(f"- Horizon: {obj['horizon']} ({obj['days_to_horizon']} days)")
        else:
            lines.append("- Horizon: ⚠ missing")
        if obj["newest_evidence"]:
            lines.append(
                f"- Newest evidence: {obj['newest_evidence']} "
                f"({obj['days_since_evidence']} days ago)"
            )
        else:
            lines.append("- Newest evidence: none found under its Evidence paths")
        if obj["missing_fields"]:
            lines.append(f"- ⚠ Missing fields: {', '.join(obj['missing_fields'])}")
        lines.append("")

    if report["horizon_soon"]:
        lines.extend(["## Horizon within 14 days", ""])
        lines.extend(f"- {title}" for title in report["horizon_soon"])
        lines.append("")

    if report["past_horizon"]:
        lines.extend(["## Past horizon — retire or explicitly reopen", ""])
        lines.extend(f"- {title}" for title in report["past_horizon"])
        lines.append("")

    if report["areas_without_objectives"]:
        lines.extend(["## Areas with no active objective", ""])
        lines.append(
            "*governed by Standards this cycle — informational, not a gap.*"
        )
        lines.append("")
        lines.extend(f"- {area}" for area in report["areas_without_objectives"])
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Global objectives review queue (all areas)"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    report = build_report(REPO_ROOT, date.today())
    print(json.dumps(report, indent=2) if args.json else render(report))


if __name__ == "__main__":
    main()
