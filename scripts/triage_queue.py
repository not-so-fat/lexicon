#!/usr/bin/env python3
"""
List untriaged Ideas/Clippings for triage (optional date filter).

Triage is interactive — Ideas queue only. Meetings are recap context, not queued.
Use --since / --until when the user specifies a period during triage.

Usage:
  python3 scripts/triage_queue.py --project personal
  python3 scripts/triage_queue.py --project acme --since 2026-04-01 --until 2026-05-24
  python3 scripts/triage_queue.py --project acme --json

Exit 0. Writes human-readable report to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
RECAP_SECTION_RE = re.compile(
    r"^## (\d{4}-\d{2}-\d{2}) triage\s*$", re.MULTILINE
)
EVIDENCE_BULLET_DATE_RE = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2})")
MODEL_HEADING_DATE_RE = re.compile(
    r"^#\s*Current model\s*\(last updated:\s*(\d{4}-\d{2}-\d{2})\)", re.IGNORECASE | re.MULTILINE
)
STALE_DAYS = 21

SCAN_ROOTS = [
    ("Ideas", lambda project, rel: rel.parts[1:2] == (project,) if len(rel.parts) > 2 else False),
]


def parse_frontmatter(content: str) -> dict:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    result: dict = {}
    current_key = None
    list_items: list[str] = []

    for line in m.group(1).split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current_key:
                list_items.append(stripped[2:].strip().strip('"').strip("'"))
            continue
        if list_items and current_key:
            result[current_key] = list_items
            list_items = []
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            current_key = key
            if val and val not in ("|", ">", "'"):
                if val.startswith("[") and val.endswith("]"):
                    inner = val[1:-1].strip()
                    result[key] = (
                        [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
                        if inner
                        else []
                    )
                else:
                    result[key] = val
            elif val in ("", "|"):
                list_items = []

    if list_items and current_key:
        result[current_key] = list_items
    return result


def normalize_date(val) -> str:
    if not val:
        return ""
    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def file_capture_date(fpath: Path, fm: dict) -> str:
    for key in ("date", "created", "published"):
        d = normalize_date(fm.get(key))
        if d:
            return d
    m = FILENAME_DATE_RE.match(fpath.name)
    if m:
        return m.group(1)
    return ""


def is_triaged(fm: dict) -> bool:
    if "triaged" not in fm:
        return False
    val = fm.get("triaged")
    if val is None:
        return False
    if isinstance(val, list):
        return bool(val)
    return bool(str(val).strip())


def project_matches(fm: dict, folder_project: str | None, target: str) -> bool:
    proj = fm.get("project")
    if isinstance(proj, list):
        proj = proj[0] if proj else ""
    proj = str(proj).strip().lower() if proj else ""
    target_l = target.lower()
    if proj:
        return proj == target_l
    return folder_project == target_l if folder_project else False


def iter_capture_files(project: str):
    """Yield (relpath, fm, capture_date, kind) for candidate capture files."""
    for root_name, path_filter in SCAN_ROOTS:
        base = REPO_ROOT / root_name
        if not base.is_dir():
            continue
        for fpath in base.rglob("*.md"):
            if fpath.name.startswith("."):
                continue
            if fpath.name.lower() == "readme.md":
                continue
            rel = fpath.relative_to(REPO_ROOT)
            parts = rel.parts
            folder_project = parts[1] if len(parts) > 2 else None

            if root_name == "Ideas" and folder_project != project:
                if folder_project == project:
                    pass
                else:
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="replace")[:8192]
                    except OSError:
                        continue
                    fm = parse_frontmatter(content)
                    if not project_matches(fm, folder_project, project):
                        continue
                    capture_date = file_capture_date(fpath, fm)
                    yield str(rel), fm, capture_date, root_name
                    continue

            if not path_filter(project, rel):
                continue

            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")[:8192]
            except OSError:
                continue
            fm = parse_frontmatter(content)
            if not project_matches(fm, folder_project, project):
                continue
            capture_date = file_capture_date(fpath, fm)
            yield str(rel), fm, capture_date, root_name

    clippings = REPO_ROOT / "Clippings"
    if clippings.is_dir():
        for fpath in clippings.rglob("*.md"):
            if fpath.name.lower() == "readme.md":
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")[:8192]
            except OSError:
                continue
            fm = parse_frontmatter(content)
            if not project_matches(fm, None, project):
                continue
            rel = fpath.relative_to(REPO_ROOT)
            yield str(rel), fm, file_capture_date(fpath, fm), "Clippings"


def in_date_range(capture_date: str, since: str | None, until: str | None) -> bool:
    if not since and not until:
        return True
    if not capture_date:
        return not since
    if since and capture_date < since:
        return False
    if until and capture_date > until:
        return False
    return True


def load_last_recap(project: str) -> tuple[str, str]:
    """Return (recap_file_relpath, last_section_text) or ('', '')."""
    recap_dir = REPO_ROOT / "Metadata" / "recap" / project
    if not recap_dir.is_dir():
        return "", ""

    recap_files = sorted(recap_dir.glob("*.md"), reverse=True)
    recap_files = [f for f in recap_files if f.name.lower() != "readme.md"]
    if not recap_files:
        return "", ""

    latest = recap_files[0]
    try:
        text = latest.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", ""

    matches = list(RECAP_SECTION_RE.finditer(text))
    if not matches:
        return str(latest.relative_to(REPO_ROOT)), text.strip()[-2000:]

    last = matches[-1]
    section = text[last.start() :].strip()
    return str(latest.relative_to(REPO_ROOT)), section


OPEN_DECISION_LINE_RE = re.compile(
    r"^\s*-\s*(\d{4}-\d{2}-\d{2})\s*—\s*(?:Pending(?: decision)?(?:\s*\([^)]*\))?:?\s*)?",
    re.IGNORECASE,
)


def _open_decisions_from_file(
    path: Path, source_label: str, section_header: str = "## open decisions"
) -> list[str]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    in_open = False
    found: list[str] = []
    target = section_header.strip().lower()
    for ln in lines:
        if ln.strip().lower() == target:
            in_open = True
            continue
        if in_open and ln.startswith("#"):
            break
        if not in_open:
            continue
        stripped = ln.strip()
        if not stripped.startswith("-"):
            continue
        if (
            "pending" in stripped.lower()
            or "testing:" in stripped.lower()
            or OPEN_DECISION_LINE_RE.match(stripped)
        ):
            found.append(f"[{source_label}] {stripped.lstrip('-').strip()}")
    return found


def _pending_from_decisions_log(path: Path) -> list[str]:
    """Classic layout: Memory/<project>/Decisions/decisions.md."""
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    found: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if not stripped.startswith("-"):
            continue
        lower = stripped.lower()
        if "pending decision" in lower or "decision (pending)" in lower:
            found.append(f"[Decisions] {stripped.lstrip('-').strip()}")
    return found


def pending_decisions_snippet(project: str, limit: int = 20) -> list[str]:
    memory = REPO_ROOT / "Memory" / project
    pending: list[str] = []

    validation = memory / "Validation.md"
    pending.extend(
        _open_decisions_from_file(validation, "Validation", "## open hypotheses")
    )

    for area in ("Org.md", "Product.md"):
        pending.extend(_open_decisions_from_file(memory / area, area.replace(".md", "")))

    partners_dir = memory / "Partners"
    if partners_dir.is_dir():
        for partner_file in sorted(partners_dir.glob("*.md")):
            if partner_file.name.lower() in ("index.md", "readme.md"):
                continue
            label = f"Partners/{partner_file.stem}"
            pending.extend(_open_decisions_from_file(partner_file, label))

    legacy = memory / "_legacy" / "decisions.md"
    if legacy.is_file():
        try:
            lines = legacy.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            lines = []
        for ln in lines:
            if "pending decision" in ln.lower():
                pending.append(f"[legacy decisions] {ln.strip().lstrip('-').strip()}")

    pending.extend(_pending_from_decisions_log(memory / "Decisions" / "decisions.md"))

    return pending[-limit:]


def _all_bullet_dates(text: str) -> list[str]:
    return sorted(
        m.group(1) for ln in text.splitlines() if (m := EVIDENCE_BULLET_DATE_RE.match(ln))
    )


def _inline_evidence(text: str) -> tuple[bool, list[str]]:
    """Legacy inline `# Evidence` section in a model file: (present, bullet dates)."""
    in_section = False
    present = False
    dates: list[str] = []
    for ln in text.splitlines():
        stripped = ln.strip().lower()
        if stripped.startswith("# evidence"):
            in_section = True
            present = True
            continue
        if in_section and ln.startswith("# "):
            in_section = False
            continue
        if in_section:
            m = EVIDENCE_BULLET_DATE_RE.match(ln)
            if m:
                dates.append(m.group(1))
    return present, sorted(dates)


def _model_updated(text: str) -> str:
    fm = parse_frontmatter(text)
    d = normalize_date(fm.get("model_updated"))
    if d:
        return d
    m = MODEL_HEADING_DATE_RE.search(text)
    return m.group(1) if m else ""


def _days_between(older: str, newer: str) -> int:
    return (
        datetime.strptime(newer, "%Y-%m-%d") - datetime.strptime(older, "%Y-%m-%d")
    ).days


def _area_model_files(project: str) -> list[Path]:
    memory = REPO_ROOT / "Memory" / project
    files: list[Path] = []
    skip = {"readme.md", "index.md", "direction.md"}
    if memory.is_dir():
        for p in sorted(memory.glob("*.md")):
            if p.name.lower() in skip or p.name.endswith(".evidence.md"):
                continue
            files.append(p)
        partners = memory / "Partners"
        if partners.is_dir():
            for p in sorted(partners.glob("*.md")):
                if p.name.lower() in skip or p.name.endswith(".evidence.md"):
                    continue
                files.append(p)
    return files


def evidence_debt(project: str) -> dict:
    """Per-area un-drained evidence + staleness, plus legacy flags.

    Un-drained = evidence bullets dated after `model_updated`. Stale = current
    model lags newest evidence by more than STALE_DAYS (or has no date at all).
    """
    areas: list[dict] = []
    for model_path in _area_model_files(project):
        try:
            model_text = model_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sibling = model_path.with_name(model_path.stem + ".evidence.md")
        sibling_dates: list[str] = []
        if sibling.is_file():
            try:
                sibling_dates = _all_bullet_dates(
                    sibling.read_text(encoding="utf-8", errors="replace")
                )
            except OSError:
                pass
        inline_present, inline_dates = _inline_evidence(model_text)
        all_dates = sorted(sibling_dates + inline_dates)
        if not all_dates and not inline_present:
            continue

        model_date = _model_updated(model_text)
        undrained = [d for d in all_dates if not model_date or d > model_date]
        newest = all_dates[-1] if all_dates else ""
        lag_days = _days_between(model_date, newest) if model_date and newest else None
        stale = bool(all_dates) and (not model_date or (lag_days or 0) > STALE_DAYS)

        rel = str(model_path.relative_to(REPO_ROOT / "Memory" / project))
        areas.append(
            {
                "area": rel.removesuffix(".md"),
                "model_updated": model_date,
                "newest_evidence": newest,
                "undrained_count": len(undrained),
                "oldest_undrained": undrained[0] if undrained else "",
                "lag_days": lag_days,
                "stale": stale,
                "inline_legacy": inline_present,
            }
        )

    legacy_dir = REPO_ROOT / "Memory" / project / "_legacy"
    legacy_files = (
        sum(1 for p in legacy_dir.rglob("*") if p.is_file()) if legacy_dir.is_dir() else 0
    )
    return {"areas": areas, "legacy_files": legacy_files}


def iter_recent_meetings(
    project: str, since: str | None, until: str | None, limit: int = 25
) -> list[dict]:
    """Recent meeting notes for triage recap context (not in queue)."""
    meetings_dir = REPO_ROOT / "Meetings" / project
    if not meetings_dir.is_dir():
        return []
    items: list[dict] = []
    for fpath in meetings_dir.glob("*.md"):
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")[:8192]
        except OSError:
            continue
        fm = parse_frontmatter(content)
        capture_date = file_capture_date(fpath, fm)
        if not in_date_range(capture_date, since, until):
            continue
        rel = str(fpath.relative_to(REPO_ROOT))
        items.append(
            {
                "path": rel,
                "date": capture_date or "(undated)",
                "title": fm.get("title", fpath.stem),
            }
        )
    items.sort(key=lambda x: (x["date"] == "(undated)", x["date"]), reverse=True)
    return items[:limit]


def build_queue(project: str, since: str | None, until: str | None) -> list[dict]:
    queue = []
    for relpath, fm, capture_date, kind in iter_capture_files(project):
        if is_triaged(fm):
            continue
        if not in_date_range(capture_date, since, until):
            continue
        queue.append(
            {
                "path": relpath,
                "kind": kind,
                "date": capture_date or "(undated)",
                "status": fm.get("status", ""),
                "title": fm.get("title", Path(relpath).stem),
            }
        )
    queue.sort(key=lambda x: (x["date"] == "(undated)", x["date"], x["path"]), reverse=True)
    return queue


def main():
    parser = argparse.ArgumentParser(description="Lexicon triage queue for a project")
    parser.add_argument("--project", required=True, help="Project slug (e.g. personal, acme)")
    parser.add_argument("--since", help="Include capture on/after YYYY-MM-DD")
    parser.add_argument("--until", help="Include capture on/before YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)

    for label, val in (("since", args.since), ("until", args.until)):
        if val and not normalize_date(val):
            print(f"Invalid --{label} date: {val}", file=sys.stderr)
            sys.exit(1)

    since = normalize_date(args.since) if args.since else None
    until = normalize_date(args.until) if args.until else None

    queue = build_queue(args.project, since, until)
    recent_meetings = iter_recent_meetings(args.project, since, until)
    recap_path, last_section = load_last_recap(args.project)
    pending = pending_decisions_snippet(args.project)
    debt = evidence_debt(args.project)

    if args.json:
        print(
            json.dumps(
                {
                    "project": args.project,
                    "since": since,
                    "until": until,
                    "queue_count": len(queue),
                    "queue": queue,
                    "recent_meetings": recent_meetings,
                    "last_recap_file": recap_path,
                    "last_recap_section": last_section,
                    "pending_decisions": pending,
                    "evidence_debt": debt,
                },
                indent=2,
            )
        )
        return

    lines = [
        f"# Triage queue — {args.project}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]
    if since or until:
        lines.append(f"Period filter: {since or '…'} → {until or '…'}")
    else:
        lines.append("Period filter: none (all untriaged ideas/clippings for project)")
    lines.append(f"Untriaged ideas queue: **{len(queue)}**")
    lines.append("")
    lines.append(
        "*Meetings are not triaged — use distill after summarize. Listed below for recap context only.*"
    )

    if recap_path and last_section:
        lines.extend(
            [
                "## Previous triage (remind user)",
                f"From: `{recap_path}`",
                "",
                last_section,
                "",
            ]
        )
    else:
        lines.extend(["## Previous triage", "(none yet — first triage for this project)", ""])

    if pending:
        lines.extend(["## Pending decisions (carry forward)", ""])
        for p in pending:
            lines.append(f"- {p}")
        lines.append("")

    if debt["areas"] or debt["legacy_files"]:
        lines.extend(["## Evidence debt (drain in Memory step — or defer explicitly)", ""])
        for a in debt["areas"]:
            parts = [f"- **{a['area']}**"]
            if a["undrained_count"]:
                oldest = f" (oldest {a['oldest_undrained']})" if a["oldest_undrained"] else ""
                plural = "s" if a["undrained_count"] != 1 else ""
                parts.append(f" — {a['undrained_count']} un-drained bullet{plural}{oldest}")
            else:
                parts.append(" — drained")
            if a["model_updated"]:
                parts.append(f"; model updated {a['model_updated']}")
            else:
                parts.append("; model has no `model_updated:` date")
            if a["newest_evidence"]:
                parts.append(f", newest evidence {a['newest_evidence']}")
            if a["stale"]:
                lag = f" ({a['lag_days']} days behind)" if a["lag_days"] is not None else ""
                parts.append(f" ⚠ STALE{lag}")
            if a["inline_legacy"]:
                parts.append(
                    f" — inline `# Evidence` (legacy): migrate to {a['area']}.evidence.md"
                )
            lines.append("".join(parts))
        if debt["legacy_files"]:
            lines.append(
                f"- **_legacy/** contains {debt['legacy_files']} file(s) — migrate or archive"
            )
        lines.append("")

    if recent_meetings:
        lines.extend(["## Recent meetings (recap context — read only)", ""])
        for item in recent_meetings:
            lines.append(f"- {item['date']} | [{item['title']}]({item['path']})")
        lines.append("")

    lines.extend(["## Ideas queue (untriaged)", ""])
    if not queue:
        lines.append("(empty — nothing to triage for this filter)")
    else:
        by_kind: dict[str, list] = {}
        for item in queue:
            by_kind.setdefault(item["kind"], []).append(item)
        for kind in sorted(by_kind.keys()):
            lines.append(f"### {kind}")
            for item in by_kind[kind]:
                lines.append(f"- {item['date']} | [{item['title']}]({item['path']})")
            lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
