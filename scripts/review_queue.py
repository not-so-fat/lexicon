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
DUE_SOON_DAYS = 14
REVIEW_STALE_DAYS = 14
DIRECTION_STALE_DAYS = 60

OBJ_HEADING_RE = re.compile(r"^###\s+(?:(\[WIG\])\s+)?(.+?)\s*$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
FIELD_RE = re.compile(r"^\s*-\s+\*\*(?P<key>[^:*]+):\*\*\s*(?P<val>.*?)\s*$")
DATED_BULLET_RE = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2})")
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
REVIEW_FILE_RE = re.compile(r"^(\d{4})-W(\d{2})\.md$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")

REQUIRED_FIELDS = ("area", "by", "done when", "obstacle", "evidence", "opened")


def unfenced_lines(text: str) -> list[str]:
    """`text`'s lines with fenced code blocks (and their marker lines) removed.

    Shared by `parse_objectives` (here) and `lint_direction` (`lint_vault.py`) —
    both are line-by-line Markdown scanners that must not treat fenced worked
    examples as live content. One state machine, two callers, so this species
    of bug (a scanner blind to what encloses the line) can't recur by drifting
    copies out of sync.

    A fence opens on a marker line (```` ``` ```` or `~~~`, up to 3 leading
    spaces, optional info string) and closes on a line with the same character,
    at least as long, followed by nothing but whitespace (CommonMark). An
    unterminated fence runs to EOF, matching how Markdown itself renders it.
    """
    out: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if m:
            marker, trailing = m.group(1), m.group(2)
            if fence_char is None:
                # Opening a fence — an info string (e.g. ```python) is allowed.
                fence_char, fence_len = marker[0], len(marker)
            elif (
                marker[0] == fence_char
                and len(marker) >= fence_len
                and trailing.strip() == ""
            ):
                # Matching close: same char, >= opening length, and nothing but
                # whitespace after the marker — a marker line carrying an info
                # string (e.g. a nested worked example's own opening fence)
                # does not close us.
                fence_char, fence_len = None, 0
            continue
        if fence_char is not None:
            continue
        out.append(line)
    return out


def objective_cap() -> int:
    raw = os.environ.get("LEXICON_OBJECTIVE_CAP", "")
    try:
        return int(raw) if raw.strip() else DEFAULT_CAP
    except ValueError:
        return DEFAULT_CAP


def parse_objectives(text: str) -> list[dict]:
    """Objectives under `## Active`. Everything after the next `##` is ignored.

    HTML comments (`<!-- ... -->`, single- or multi-line) are stripped first,
    so a commented-out example — the shipped scaffold's convention for an
    inert placeholder — is never parsed as a live objective. Fenced code
    blocks are then dropped via `unfenced_lines` — the docs present the
    objective schema inside a ```markdown fence (docs/OBJECTIVES.md), so a
    worked example copied verbatim must not parse as a live objective, and a
    fenced `## ` line must not be mistaken for the end of `## Active` and
    silently truncate every objective after it.
    """
    text = HTML_COMMENT_RE.sub("", text)
    objectives: list[dict] = []
    current: dict | None = None
    in_active = False

    for line in unfenced_lines(text):
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
        obj["by"] = normalize_date(fields.get("by", ""))
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


def direction_health(root: Path, today: date) -> list[dict]:
    """Age of each Direction file — flags ones due a reaffirm pass in review."""
    out: list[dict] = []
    direction = root / "Direction"
    if not direction.is_dir():
        return out
    for path in sorted(direction.glob("*.md")):
        if path.stem.lower() in ("readme", "index"):
            continue
        fm_text = path.read_text(encoding="utf-8", errors="replace")
        from triage_queue import parse_frontmatter  # local import avoids cycle at module load
        updated = normalize_date(parse_frontmatter(fm_text).get("direction_updated"))
        days = _days_between(updated, today)
        out.append(
            {
                "file": str(path.relative_to(root)),
                "direction_updated": updated,
                "days_since_update": days,
                "stale": days is None or days > DIRECTION_STALE_DAYS,
            }
        )
    return out


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
    try:
        return (later - date.fromisoformat(earlier)).days
    except ValueError:
        # A malformed date (e.g. a typo'd `2026-13-45` evidence bullet) must
        # not take down the whole queue — treat it as "no date" rather than
        # crashing on a value DATED_BULLET_RE's regex doesn't validate.
        return None


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
        if obj["by"]:
            obj["days_until_due"] = (date.fromisoformat(obj["by"]) - today).days
            obj["overdue"] = obj["days_until_due"] < 0
        else:
            obj["days_until_due"] = None
            obj["overdue"] = False
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
        "due_soon": [
            obj["title"]
            for obj in objectives
            if obj["days_until_due"] is not None
            and 0 <= obj["days_until_due"] <= DUE_SOON_DAYS
        ],
        "overdue": [obj["title"] for obj in objectives if obj["overdue"]],
        "last_review_date": effective_review,
        "last_review_path": review_path,
        "days_since_review": days_since_review,
        "review_stale": days_since_review is None or days_since_review > REVIEW_STALE_DAYS,
        "areas_without_objectives": [a for a in known_areas(root) if a not in areas_with],
        "direction_health": direction_health(root, today),
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
        if obj["by"]:
            if obj["overdue"]:
                lines.append(
                    f"- By: {obj['by']} ⚠ passed "
                    f"{abs(obj['days_until_due'])} days ago — retire or reopen"
                )
            else:
                lines.append(f"- By: {obj['by']} ({obj['days_until_due']} days)")
        else:
            lines.append("- By: ⚠ missing")
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

    if report["due_soon"]:
        lines.extend(["## Due within 14 days", ""])
        lines.extend(f"- {title}" for title in report["due_soon"])
        lines.append("")

    if report["overdue"]:
        lines.extend(["## Overdue — retire or explicitly reopen", ""])
        lines.extend(f"- {title}" for title in report["overdue"])
        lines.append("")

    if report["direction_health"]:
        lines.extend(["## Direction health", ""])
        lines.append(
            "*Stale files get a reaffirm pass this session: re-read Principles/Standards"
            " with the user — reaffirm (restamp `direction_updated:`), amend, or retire items.*"
        )
        lines.append("")
        for d in report["direction_health"]:
            if d["direction_updated"]:
                age = f"updated {d['direction_updated']} ({d['days_since_update']} days ago)"
            else:
                age = "no `direction_updated:` stamp"
            flag = " ⚠ reaffirm" if d["stale"] else ""
            lines.append(f"- `{d['file']}` — {age}{flag}")
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
