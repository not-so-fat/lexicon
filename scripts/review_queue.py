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
