#!/usr/bin/env python3
"""
List HiDock transcripts in Transcripts/HiDock/ that have no meeting note yet.

Pending = no Meetings/**/*.md references the transcript (by signature, basename, or wikilink).

Usage:
  python scripts/hidock_pending.py list
  python scripts/hidock_pending.py list --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
HIDOCK_DIR = os.path.join(REPO_ROOT, "Transcripts", "HiDock")
MEETINGS_DIR = os.path.join(REPO_ROOT, "Meetings")

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
SIGNATURE_RE = re.compile(r"^signature:\s*['\"]?(\S+?)['\"]?\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
DATE_RE = re.compile(r"^date:\s*['\"]?(\S+?)['\"]?\s*$", re.MULTILINE)
HIDOCK_SIG_FM_RE = re.compile(r"^hidock_signature:\s*['\"]?(\S+?)['\"]?\s*$", re.MULTILINE)
HIDOCK_PATH_RE = re.compile(r"Transcripts/HiDock/([^\]\s\)\|\"']+)", re.IGNORECASE)


def _read_frontmatter(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        head = f.read(8192)
    match = FRONTMATTER_RE.match(head)
    return match.group(1) if match else ""


def _parse_transcript(path: str) -> dict | None:
    fm = _read_frontmatter(path)
    sig_match = SIGNATURE_RE.search(fm)
    if not sig_match:
        return None
    signature = sig_match.group(1).strip()
    basename = os.path.basename(path)
    stem = basename[:-3] if basename.endswith(".md") else basename
    short_id = stem.rsplit("_", 1)[-1] if "_" in stem else ""
    title_match = TITLE_RE.search(fm)
    date_match = DATE_RE.search(fm)
    title = (title_match.group(1).strip().strip('"').strip("'") if title_match else stem)
    date_raw = date_match.group(1).strip() if date_match else ""
    rel = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
    return {
        "path": rel,
        "basename": basename,
        "stem": stem,
        "signature": signature,
        "short_id": short_id,
        "title": title,
        "date": date_raw.replace("/", "-") if date_raw else "",
    }


def _collect_summarized_keys() -> set[str]:
    keys: set[str] = set()
    if not os.path.isdir(MEETINGS_DIR):
        return keys

    for root, _dirs, files in os.walk(MEETINGS_DIR):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except OSError:
                continue

            fm = _read_frontmatter(path)
            for match in HIDOCK_SIG_FM_RE.finditer(fm):
                keys.add(match.group(1).strip().lower())

            for match in HIDOCK_PATH_RE.finditer(text):
                ref = match.group(1).strip().rstrip("/")
                keys.add(ref.lower())
                if ref.endswith(".md"):
                    ref = ref[:-3]
                keys.add(ref.lower())
                if "_" in ref:
                    keys.add(ref.rsplit("_", 1)[-1].lower())

    return keys


def _is_summarized(meta: dict, summarized_keys: set[str]) -> bool:
    candidates = {
        meta["signature"].lower(),
        meta["basename"].lower(),
        meta["stem"].lower(),
        meta["path"].lower(),
        meta["short_id"].lower(),
    }
    if len(meta["signature"]) >= 8:
        candidates.add(meta["signature"][:8].lower())
    return bool(candidates & summarized_keys)


def list_pending() -> list[dict]:
    if not os.path.isdir(HIDOCK_DIR):
        return []

    summarized_keys = _collect_summarized_keys()
    pending: list[dict] = []

    for name in sorted(os.listdir(HIDOCK_DIR)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(HIDOCK_DIR, name)
        meta = _parse_transcript(path)
        if meta is None:
            continue
        if not _is_summarized(meta, summarized_keys):
            pending.append(meta)

    pending.sort(key=lambda m: (m.get("date") or "", m.get("path") or ""), reverse=True)
    return pending


def main() -> None:
    parser = argparse.ArgumentParser(description="List HiDock transcripts pending summarize")
    sub = parser.add_subparsers(dest="command", required=True)
    list_p = sub.add_parser("list", help="List transcripts without a meeting note")
    list_p.add_argument("--json", action="store_true", help="Print JSON array")
    args = parser.parse_args()

    pending = list_pending()
    if args.json:
        print(json.dumps(pending, indent=2))
        return

    if not pending:
        print("No pending HiDock transcripts.")
        return

    print(f"Pending HiDock transcripts ({len(pending)}):")
    for item in pending:
        date = item.get("date") or "?"
        print(f"  {date}  {item['title']}  →  {item['path']}")


if __name__ == "__main__":
    main()
