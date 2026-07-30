#!/usr/bin/env python3
"""
Triage queue for an area — deterministic inputs for the interactive session.

Reports (counts and dates only; judgment happens in the session):
  - previous triage recap
  - synthesis staleness (`synthesized:` stamp vs newest evidence bullet)
  - new evidence since the stamp, incl. `Pending decision:` bullets to promote
  - open decision files and overdue `decide-by` dates
  - pending entity-correction proposals (Metadata/entity_registry.md)
  - recent meetings (recap context — never queued)
  - untriaged Ideas/Clippings
  - usage summary (if Metadata/usage/access.jsonl exists)

Usage:
  python3 scripts/triage_queue.py --area personal
  python3 scripts/triage_queue.py --area acme --since 2026-04-01 --until 2026-05-24
  python3 scripts/triage_queue.py --area acme --json

Exit 0. Writes human-readable report to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
RECAP_SECTION_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2}) triage\s*$", re.MULTILINE)
EVIDENCE_BULLET_DATE_RE = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2})")
PENDING_DECISION_RE = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2})\s*[—-]\s*Pending decision:", re.IGNORECASE)
STALE_DAYS = 21
USAGE_WINDOW_DAYS = 30

IDEAS_ROOT = ("Sources", "Ideas")
CLIPPINGS_ROOT = ("Sources", "Clippings")
MEETINGS_ROOT = ("Sources", "Meetings")


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


def area_matches(fm: dict, folder_area: str | None, target: str) -> bool:
    val = fm.get("area")
    if val is None:
        val = fm.get("project")  # legacy key — readers accept it forever
    if isinstance(val, list):
        val = val[0] if val else ""
    val = str(val).strip().lower() if val else ""
    target_l = target.lower()
    if val:
        return val == target_l
    return folder_area == target_l if folder_area else False


def _read_head(fpath: Path, limit: int = 8192) -> str | None:
    try:
        return fpath.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return None


def iter_capture_files(area: str):
    """Yield (relpath, fm, capture_date, kind) for untriaged-candidate files."""
    ideas = REPO_ROOT.joinpath(*IDEAS_ROOT)
    if ideas.is_dir():
        for fpath in ideas.rglob("*.md"):
            if fpath.name.startswith(".") or fpath.name.lower() == "readme.md":
                continue
            rel = fpath.relative_to(REPO_ROOT)
            folder_area = rel.parts[2] if len(rel.parts) > 3 else None
            content = _read_head(fpath)
            if content is None:
                continue
            fm = parse_frontmatter(content)
            if not area_matches(fm, folder_area, area):
                continue
            yield str(rel), fm, file_capture_date(fpath, fm), "Ideas"

    clippings = REPO_ROOT.joinpath(*CLIPPINGS_ROOT)
    if clippings.is_dir():
        for fpath in clippings.rglob("*.md"):
            if fpath.name.lower() == "readme.md":
                continue
            content = _read_head(fpath)
            if content is None:
                continue
            fm = parse_frontmatter(content)
            if not area_matches(fm, None, area):
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


def load_last_recap(area: str) -> tuple[str, str]:
    """Return (recap_file_relpath, last_section_text) or ('', '')."""
    recap_dir = REPO_ROOT / "Metadata" / "recap" / area
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
    section = text[last.start():].strip()
    return str(latest.relative_to(REPO_ROOT)), section


def _days_between(older: str, newer: str) -> int:
    return (
        datetime.strptime(newer, "%Y-%m-%d") - datetime.strptime(older, "%Y-%m-%d")
    ).days


def synthesis_status(area: str) -> dict:
    """Stamp vs evidence: what has accumulated since the last rewrite."""
    synth_path = REPO_ROOT / "Synthesis" / f"{area}.md"
    stamp = ""
    if synth_path.is_file():
        fm = parse_frontmatter(synth_path.read_text(encoding="utf-8", errors="replace"))
        stamp = normalize_date(fm.get("synthesized"))

    evidence_dir = REPO_ROOT / "Evidence" / area
    per_file: list[dict] = []
    newest = ""
    pending: list[str] = []
    if evidence_dir.is_dir():
        for fpath in sorted(evidence_dir.rglob("*.md")):
            if fpath.name.lower() == "readme.md":
                continue
            try:
                lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            new_count = 0
            file_newest = ""
            for ln in lines:
                m = EVIDENCE_BULLET_DATE_RE.match(ln)
                if not m:
                    continue
                d = m.group(1)
                file_newest = max(file_newest, d)
                if not stamp or d > stamp:
                    new_count += 1
                    if PENDING_DECISION_RE.match(ln):
                        pending.append(ln.strip().lstrip("-").strip())
            newest = max(newest, file_newest)
            if new_count:
                per_file.append(
                    {
                        "path": str(fpath.relative_to(REPO_ROOT)),
                        "new_bullets": new_count,
                        "newest": file_newest,
                    }
                )

    lag = _days_between(stamp, newest) if stamp and newest else None
    stale = bool(newest) and (not stamp or (lag or 0) > STALE_DAYS)
    return {
        "synthesis_file": str(synth_path.relative_to(REPO_ROOT)) if synth_path.is_file() else "",
        "synthesized": stamp,
        "newest_evidence": newest,
        "lag_days": lag,
        "stale": stale,
        "new_evidence": per_file,
        "pending_decision_bullets": pending,
    }


def open_decisions(area: str, today: str) -> list[dict]:
    """Decision-state files that are open or held, with overdue flags."""
    ddir = REPO_ROOT / "Synthesis" / area / "decisions"
    out: list[dict] = []
    if not ddir.is_dir():
        return out
    for fpath in sorted(ddir.glob("*.md")):
        if fpath.name.lower() == "readme.md":
            continue
        try:
            fm = parse_frontmatter(fpath.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        status = str(fm.get("status", "")).strip().lower()
        if status in ("committed", "killed"):
            continue
        decide_by = normalize_date(fm.get("decide-by") or fm.get("decide_by"))
        out.append(
            {
                "path": str(fpath.relative_to(REPO_ROOT)),
                "status": status or "(no status)",
                "decide_by": decide_by,
                "overdue": bool(decide_by) and decide_by < today,
            }
        )
    return out


def usage_summary(area: str, today: datetime) -> dict:
    """Reads-per-tier for this area from the usage log, last USAGE_WINDOW_DAYS."""
    log = REPO_ROOT / "Metadata" / "usage" / "access.jsonl"
    if not log.is_file():
        return {}
    cutoff = (today - timedelta(days=USAGE_WINDOW_DAYS)).strftime("%Y-%m-%d")
    tiers: dict[str, int] = {}
    files: dict[str, int] = {}
    try:
        for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            ts = str(entry.get("ts", ""))[:10]
            path = str(entry.get("path", ""))
            if ts < cutoff or not path:
                continue
            tier = path.split("/", 1)[0]
            if area.lower() not in path.lower() and tier not in ("Direction", "Objectives.md"):
                continue
            tiers[tier] = tiers.get(tier, 0) + 1
            files[path] = files.get(path, 0) + 1
    except OSError:
        return {}
    top = sorted(files.items(), key=lambda kv: -kv[1])[:5]
    return {"window_days": USAGE_WINDOW_DAYS, "reads_by_tier": tiers, "top_files": top}


def pending_entity_proposals() -> list[str]:
    """Dated bullets under `## Proposed` in Metadata/entity_registry.md."""
    path = REPO_ROOT / "Metadata" / "entity_registry.md"
    if not path.is_file():
        return []
    out: list[str] = []
    in_section = False
    in_comment = False
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.strip()
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("<!--"):
            in_comment = "-->" not in s
            continue
        if s.lower().startswith("## proposed"):
            in_section = True
            continue
        if in_section and s.startswith("#"):
            break
        if in_section and s.startswith("-"):
            out.append(s.lstrip("-").strip())
    return out


def iter_recent_meetings(
    area: str, since: str | None, until: str | None, limit: int = 25
) -> list[dict]:
    """Recent meeting notes for triage recap context (not in queue)."""
    meetings_dir = REPO_ROOT.joinpath(*MEETINGS_ROOT) / area
    if not meetings_dir.is_dir():
        return []
    items: list[dict] = []
    for fpath in meetings_dir.glob("*.md"):
        content = _read_head(fpath)
        if content is None:
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


def build_queue(area: str, since: str | None, until: str | None) -> list[dict]:
    queue = []
    for relpath, fm, capture_date, kind in iter_capture_files(area):
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
    parser = argparse.ArgumentParser(description="Lexicon triage queue for an area")
    parser.add_argument("--area", dest="area", help="Area slug (e.g. personal, acme)")
    parser.add_argument("--project", dest="area", help=argparse.SUPPRESS)  # deprecated alias
    parser.add_argument("--since", help="Include capture on/after YYYY-MM-DD")
    parser.add_argument("--until", help="Include capture on/before YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not args.area:
        parser.error("--area is required (or its deprecated alias --project)")

    os.chdir(REPO_ROOT)

    for label, val in (("since", args.since), ("until", args.until)):
        if val and not normalize_date(val):
            print(f"Invalid --{label} date: {val}", file=sys.stderr)
            sys.exit(1)

    since = normalize_date(args.since) if args.since else None
    until = normalize_date(args.until) if args.until else None

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    queue = build_queue(args.area, since, until)
    recent_meetings = iter_recent_meetings(args.area, since, until)
    recap_path, last_section = load_last_recap(args.area)
    synth = synthesis_status(args.area)
    decisions = open_decisions(args.area, today)
    entity_proposals = pending_entity_proposals()
    usage = usage_summary(args.area, now)

    if args.json:
        print(
            json.dumps(
                {
                    "area": args.area,
                    "since": since,
                    "until": until,
                    "queue_count": len(queue),
                    "queue": queue,
                    "recent_meetings": recent_meetings,
                    "last_recap_file": recap_path,
                    "last_recap_section": last_section,
                    "synthesis": synth,
                    "open_decisions": decisions,
                    "entity_proposals": entity_proposals,
                    "usage": usage,
                },
                indent=2,
            )
        )
        return

    lines = [
        f"# Triage queue — {args.area}",
        "",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M')}",
    ]
    if since or until:
        lines.append(f"Period filter: {since or '…'} → {until or '…'}")
    else:
        lines.append("Period filter: none (all untriaged ideas/clippings for area)")
    lines.append(f"Untriaged ideas queue: **{len(queue)}**")
    lines.append("")
    lines.append(
        "*Meetings are not triaged — use distill after summarize. Listed below for recap context only.*"
    )

    if recap_path and last_section:
        lines.extend(
            ["## Previous triage (remind user)", f"From: `{recap_path}`", "", last_section, ""]
        )
    else:
        lines.extend(["## Previous triage", "(none yet — first triage for this area)", ""])

    lines.extend(["## Synthesis status", ""])
    if synth["synthesis_file"]:
        stamp = synth["synthesized"] or "⚠ no `synthesized:` stamp"
        lines.append(f"- `{synth['synthesis_file']}` — synthesized {stamp}")
    else:
        lines.append(f"- ⚠ no `Synthesis/{args.area}.md` yet — first triage creates it")
    if synth["newest_evidence"]:
        lines.append(f"- Newest evidence: {synth['newest_evidence']}")
    if synth["stale"]:
        lag = f" ({synth['lag_days']} days behind)" if synth["lag_days"] is not None else ""
        lines.append(f"- ⚠ STALE{lag} — rewrite the synthesis this session or defer explicitly")
    for f in synth["new_evidence"]:
        plural = "s" if f["new_bullets"] != 1 else ""
        lines.append(f"- {f['path']} — {f['new_bullets']} new bullet{plural} (newest {f['newest']})")
    lines.append("")

    if synth["pending_decision_bullets"]:
        lines.extend(["## Pending decisions to promote (from evidence)", ""])
        for p in synth["pending_decision_bullets"]:
            lines.append(f"- {p}")
        lines.append("")

    if decisions:
        lines.extend(["## Open decisions", ""])
        for d in decisions:
            overdue = " ⚠ OVERDUE — decide, extend with reason, or kill" if d["overdue"] else ""
            by = d["decide_by"] or "⚠ no decide-by"
            lines.append(f"- `{d['path']}` — {d['status']}, decide-by {by}{overdue}")
        lines.append("")

    if entity_proposals:
        lines.extend(["## Entity corrections (approve into Canonical or reject)", ""])
        for e in entity_proposals:
            lines.append(f"- {e}")
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

    if usage:
        lines.extend([f"## Usage (last {usage['window_days']} days)", ""])
        for tier, n in sorted(usage["reads_by_tier"].items(), key=lambda kv: -kv[1]):
            lines.append(f"- {tier}: {n} reads")
        if usage["top_files"]:
            lines.append("- Top files: " + ", ".join(f"`{p}` ({n})" for p, n in usage["top_files"]))
        lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
