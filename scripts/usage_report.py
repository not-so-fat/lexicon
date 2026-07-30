#!/usr/bin/env python3
"""
Aggregate Metadata/usage/access.jsonl — the reporting side of the usage QA
layer (docs/MEMORY_MODEL.md). Answers, with data instead of opinion:

  - How often is each tier actually consumed?
  - Are the constant inputs (Direction/, Objectives.md) read every session?
  - Which evidence and synthesis files are never consulted?
  - Is any lens ever fired?

Usage:
  python3 scripts/usage_report.py [--days 30] [--area <area>] [--json]

Exit 0 always. No log file yet → says so and exits (wire scripts/log_usage.py
as a PostToolUse hook first).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LOG_FILE = REPO_ROOT / "Metadata" / "usage" / "access.jsonl"

TIER_ROOTS = ("Direction", "Synthesis", "Evidence", "Sources")


def load_entries(days: int) -> list[dict]:
    if not LOG_FILE.is_file():
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()[:10]
    entries = []
    for raw in LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if str(entry.get("ts", ""))[:10] >= cutoff and entry.get("path"):
            entries.append(entry)
    return entries


def tier_of(path: str) -> str:
    if path.startswith("Objectives"):
        return "Objectives"
    return path.split("/", 1)[0]


def tracked_files(area: str | None) -> dict[str, list[str]]:
    """Existing vault files per tier — the denominator for never-read."""
    out: dict[str, list[str]] = {}
    for top in TIER_ROOTS:
        base = REPO_ROOT / top
        if not base.is_dir():
            continue
        files = []
        for p in sorted(base.rglob("*.md")):
            if p.name.lower() in ("readme.md", "index.md"):
                continue
            rel = str(p.relative_to(REPO_ROOT))
            if area and f"/{area.lower()}" not in f"/{rel.lower()}":
                continue
            files.append(rel)
        if files:
            out[top] = files
    for name in ("Objectives.md",):
        if (REPO_ROOT / name).is_file():
            out.setdefault("Objectives", []).append(name)
    return out


def build_report(days: int, area: str | None) -> dict:
    entries = load_entries(days)
    if area:
        entries = [
            e
            for e in entries
            if area.lower() in e["path"].lower() or tier_of(e["path"]) in ("Direction", "Objectives")
        ]

    reads_by_tier: dict[str, int] = {}
    reads_by_file: dict[str, int] = {}
    last_read: dict[str, str] = {}
    sessions_by_tier: dict[str, set] = {}
    for e in entries:
        tier = tier_of(e["path"])
        reads_by_tier[tier] = reads_by_tier.get(tier, 0) + 1
        reads_by_file[e["path"]] = reads_by_file.get(e["path"], 0) + 1
        last_read[e["path"]] = max(last_read.get(e["path"], ""), e["ts"][:10])
        if e.get("session"):
            sessions_by_tier.setdefault(tier, set()).add(e["session"])

    all_files = tracked_files(area)
    never_read = {
        tier: [f for f in files if f not in reads_by_file]
        for tier, files in all_files.items()
    }
    constant_inputs = [
        {
            "path": f,
            "reads": reads_by_file.get(f, 0),
            "last_read": last_read.get(f, ""),
        }
        for f in all_files.get("Direction", []) + all_files.get("Objectives", [])
    ]

    total_sessions = len({e.get("session") for e in entries if e.get("session")})
    return {
        "window_days": days,
        "entries": len(entries),
        "sessions": total_sessions,
        "reads_by_tier": reads_by_tier,
        "sessions_by_tier": {k: len(v) for k, v in sessions_by_tier.items()},
        "top_files": sorted(reads_by_file.items(), key=lambda kv: -kv[1])[:15],
        "constant_inputs": constant_inputs,
        "never_read": never_read,
    }


def render(r: dict) -> str:
    lines = [
        "# Vault usage report",
        "",
        f"Window: last {r['window_days']} days — {r['entries']} logged reads"
        + (f" across {r['sessions']} sessions" if r["sessions"] else ""),
        "",
        "## Reads by tier",
        "",
    ]
    if not r["reads_by_tier"]:
        lines.append("(no reads logged — is scripts/log_usage.py wired as a PostToolUse hook?)")
    for tier, n in sorted(r["reads_by_tier"].items(), key=lambda kv: -kv[1]):
        sessions = r["sessions_by_tier"].get(tier)
        extra = f" ({sessions} sessions)" if sessions else ""
        lines.append(f"- {tier}: {n}{extra}")
    lines.append("")

    lines.extend(["## Constant inputs — read every session?", ""])
    if not r["constant_inputs"]:
        lines.append("(no Direction files or Objectives.md found)")
    for c in r["constant_inputs"]:
        status = f"{c['reads']} reads, last {c['last_read']}" if c["reads"] else "⚠ never read in window"
        lines.append(f"- `{c['path']}` — {status}")
    lines.append("")

    if r["top_files"]:
        lines.extend(["## Most-read files", ""])
        lines.extend(f"- `{p}` — {n}" for p, n in r["top_files"])
        lines.append("")

    for tier in ("Synthesis", "Evidence", "Direction"):
        unread = r["never_read"].get(tier, [])
        if unread:
            lines.extend(
                [
                    f"## {tier} files never read in window ({len(unread)})",
                    "",
                    "*Candidates to retire, merge, or stop maintaining — decide in triage/review.*",
                    "",
                ]
            )
            lines.extend(f"- `{p}`" for p in unread[:20])
            if len(unread) > 20:
                lines.append(f"- … and {len(unread) - 20} more")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate vault usage telemetry")
    parser.add_argument("--days", type=int, default=30, help="Window in days (default 30)")
    parser.add_argument("--area", help="Limit to one area slug")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    report = build_report(args.days, args.area)
    print(json.dumps(report, indent=2) if args.json else render(report))


if __name__ == "__main__":
    main()
