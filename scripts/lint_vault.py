#!/usr/bin/env python3
"""
Lint vault hygiene — the schema layer of the QA system (docs/MEMORY_MODEL.md).

The tier IS the directory, so every check routes by path:

  Sources/    — capture files have YAML frontmatter and a date.
  Evidence/   — append-only logs: every bullet dated, one line (<= MAX_BULLET_CHARS),
                no orphaned sub-bullets or undated prose blocks.
  Synthesis/  — area files carry `synthesized:` and fit LEXICON_SYNTHESIS_CAP lines;
                decision files carry `decide-by:`, `status:` and a dated
                `## Acceptance test`.
  Direction/  — three sections only (Purpose / Principles / Standards), one-line
                ID'd dated items, LEXICON_DIRECTION_CAP lines; lenses carry their
                required sections and fit LEXICON_LENS_CAP lines.
  Objectives.md — cap, WIG, required fields, and every `Evidence:` path exists.

Errors exit 1; warnings exit 0.

Usage:
  python3 scripts/lint_vault.py [--area <area>] [--json]
  python3 scripts/lint_vault.py --files <path> [<path> ...]   # write-time gate
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import date

from review_queue import objective_cap, parse_objectives, unfenced_lines

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
DATED_BULLET_RE = re.compile(r"^-\s*\d{4}-\d{2}-\d{2}\s*[—-]")
TOP_BULLET_RE = re.compile(r"^-\s+\S")
INDENTED_LINE_RE = re.compile(r"^\s+\S")
DIRECTION_ITEM_RE = re.compile(
    r"^-\s+[PS]\d+\s+—\s+.+\(adopted\s+\d{4}-\d{2}-\d{2}[^)]*\)\s*$"
)

MAX_BULLET_CHARS = 240  # ~30 words of claim text; links/tags don't count (see _claim_text)

DEFAULT_SYNTHESIS_CAP = 120
DEFAULT_DIRECTION_CAP = 60
DEFAULT_LENS_CAP = 220

SKIP_NAMES = {"readme.md", "index.md"}
CAPTURE_ROOTS = ("Sources/Meetings", "Sources/Ideas", "Sources/Clippings")
LEGACY_ROOTS = ("Meetings", "Ideas", "Clippings", "Transcripts", "Memory", "People")

DIRECTION_ALLOWED_SECTIONS = ("purpose", "principles", "standards")
LENS_REQUIRED_SECTIONS = ("when to run this", "process", "failure-mode guards")
SYNTHESIS_ALLOWED_SECTIONS = (
    "people",
    "open decisions",
    "open hypotheses",
    "direction candidates",
)
DECISION_STATUSES = {"open", "committed", "killed", "held"}
OBJECTIVE_FIELD_LABELS = {
    "area": "Area",
    "by": "By",
    "done when": "Done when",
    "obstacle": "Obstacle",
    "evidence": "Evidence",
    "opened": "Opened",
}


def _load_dotenv_caps() -> None:
    """Vault-local cap overrides live in .env (gitignored, per-vault).

    Only LEXICON_* keys are read, and real environment variables win.
    """
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("LEXICON_") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except OSError:
        pass


def _env_cap(name: str, default: int) -> int:
    _load_dotenv_caps()
    raw = os.environ.get(name, "")
    try:
        return int(raw) if raw.strip() else default
    except ValueError:
        return default


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def frontmatter_block(text: str) -> str | None:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else None


def fm_date(fm_block: str | None, key: str) -> str:
    if not fm_block:
        return ""
    m = re.search(rf"^{key}:\s*(\d{{4}}-\d{{2}}-\d{{2}})", fm_block, re.MULTILINE)
    return m.group(1) if m else ""


def has_date(fm_block: str | None, fname: str) -> bool:
    if FILENAME_DATE_RE.match(fname):
        return True
    if not fm_block:
        return False
    return bool(re.search(r"^(date|created|published):\s*\S", fm_block, re.MULTILINE))


def _issue(level: str, rel: str, msg: str) -> dict:
    return {"level": level, "path": rel, "issue": msg}


def _skippable(path: Path) -> bool:
    return path.name.lower() in SKIP_NAMES or path.name.startswith(".")


# ---------------------------------------------------------------- Sources ----

def lint_source_file(path: Path) -> list[dict]:
    rel = str(path.relative_to(REPO_ROOT))
    if rel.startswith("Sources/Transcripts"):
        return []  # raw transcripts are ingest-owned; not linted
    issues: list[dict] = []
    text = read(path)
    fm = frontmatter_block(text)
    if fm is None:
        issues.append(_issue("error", rel, "missing YAML frontmatter"))
    if fm and re.search(r"^project:\s*\S", fm, re.MULTILINE) and not re.search(
        r"^area:\s*\S", fm, re.MULTILINE
    ):
        issues.append(
            _issue(
                "warning",
                rel,
                "legacy `project:` key — run scripts/migrate_area_key.py to rewrite as `area:`",
            )
        )
    if not has_date(fm, path.name):
        issues.append(
            _issue(
                "error",
                rel,
                "no date (frontmatter date/created or YYYY-MM-DD filename prefix)",
            )
        )
    return issues


# --------------------------------------------------------------- Evidence ----

WIKILINK_RE = re.compile(r"\[\[[^\]]*\]\]")
TAG_RE = re.compile(r"(?:^|\s)#[\w/-]+")
SOURCE_SUFFIX_RE = re.compile(r"[—-]\s*Source:.*$", re.IGNORECASE)


def _claim_text(line: str) -> str:
    """The part of an evidence bullet the length cap governs.

    Provenance is structural, not prose: the `— Source: …` suffix, wikilinks,
    and inline #tags are excluded, so a well-linked bullet is never penalized
    for citing its sources.
    """
    text = SOURCE_SUFFIX_RE.sub("", line)
    text = WIKILINK_RE.sub("", text)
    text = TAG_RE.sub(" ", text)
    return text.strip()


def lint_evidence_file(path: Path) -> list[dict]:
    rel = str(path.relative_to(REPO_ROOT))
    issues: list[dict] = []
    text = read(path)
    fm = frontmatter_block(text)
    offset = len(fm.splitlines()) + 2 if fm is not None else 0  # frontmatter is optional
    body = text.splitlines()[offset:]
    in_comment = False
    for lineno, ln in enumerate(body, offset + 1):
        stripped = ln.rstrip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.lstrip().startswith("<!--"):
            # HTML comments (e.g. migration markers, frozen legacy pointers) are inert
            if "-->" not in stripped:
                in_comment = True
            continue
        if TOP_BULLET_RE.match(stripped):
            if not DATED_BULLET_RE.match(stripped):
                issues.append(
                    _issue(
                        "error",
                        rel,
                        f"line {lineno}: evidence bullet not dated (`- YYYY-MM-DD — ...`)",
                    )
                )
            claim_len = len(_claim_text(stripped))
            if claim_len > MAX_BULLET_CHARS:
                issues.append(
                    _issue(
                        "error",
                        rel,
                        f"line {lineno}: evidence bullet claim {claim_len} chars "
                        f"(max {MAX_BULLET_CHARS}, ~30 words, links/tags excluded) — "
                        "detail belongs in the source note",
                    )
                )
        elif INDENTED_LINE_RE.match(ln):
            issues.append(
                _issue(
                    "error",
                    rel,
                    f"line {lineno}: orphaned sub-bullet / continuation — evidence bullets are one line",
                )
            )
        else:
            issues.append(
                _issue(
                    "error",
                    rel,
                    f"line {lineno}: undated block — evidence files hold only dated bullets and headings",
                )
            )
    if text.strip() and "# evidence" not in text.lower():
        issues.append(
            _issue("warning", rel, "missing `# Evidence (append-only)` heading")
        )
    return issues


# -------------------------------------------------------------- Synthesis ----

def _sections(text: str) -> list[str]:
    return [
        line[3:].strip().lower()
        for line in unfenced_lines(text)
        if line.startswith("## ")
    ]


def lint_synthesis_file(path: Path) -> list[dict]:
    rel = str(path.relative_to(REPO_ROOT))
    issues: list[dict] = []
    text = read(path)

    if path.parent.name in ("people", "partners"):
        # Per-person / per-partner reads: synthesis-tier, refreshed at triage.
        # Light contract — no cap, no stamp; content shape is the session's call.
        return issues

    if path.parent.name == "decisions":
        fm = frontmatter_block(text)
        if not fm_date(fm, "decide-by"):
            issues.append(
                _issue(
                    "error",
                    rel,
                    "decision file has no `decide-by:` date — undated forks are the failure mode",
                )
            )
        status = ""
        if fm:
            m = re.search(r"^status:\s*(\S+)", fm, re.MULTILINE)
            status = m.group(1).strip().lower() if m else ""
        if status not in DECISION_STATUSES:
            issues.append(
                _issue(
                    "error",
                    rel,
                    f"decision file needs `status:` one of {sorted(DECISION_STATUSES)}",
                )
            )
        accept = re.search(
            r"^##\s+acceptance test\s*$", text, re.IGNORECASE | re.MULTILINE
        )
        if not accept:
            issues.append(
                _issue("error", rel, "decision file has no `## Acceptance test` section")
            )
        elif not re.search(
            r"^##\s+acceptance test\s*\n+(?:.*\n)*?-\s*\d{4}-\d{2}-\d{2}",
            text,
            re.IGNORECASE | re.MULTILINE,
        ):
            issues.append(
                _issue(
                    "error",
                    rel,
                    "`## Acceptance test` has no dated entry — it must be frozen with a date",
                )
            )
        return issues

    # Area synthesis file
    fm = frontmatter_block(text)
    if not fm_date(fm, "synthesized"):
        issues.append(
            _issue("error", rel, "no `synthesized:` date — stamped on every triage rewrite")
        )
    cap = _env_cap("LEXICON_SYNTHESIS_CAP", DEFAULT_SYNTHESIS_CAP)
    n_lines = len(text.splitlines())
    if n_lines > cap:
        issues.append(
            _issue(
                "error",
                rel,
                f"{n_lines} lines exceeds synthesis cap of {cap} "
                "(LEXICON_SYNTHESIS_CAP) — the cap forces selectivity, not compaction of evidence",
            )
        )
    for name in _sections(text):
        if name not in SYNTHESIS_ALLOWED_SECTIONS:
            issues.append(
                _issue(
                    "error",
                    rel,
                    f"section `## {name}` not allowed — only People, Open decisions, "
                    "Open hypotheses, Direction candidates",
                )
            )
    return issues


# -------------------------------------------------------------- Direction ----

def lint_direction_file(path: Path) -> list[dict]:
    rel = str(path.relative_to(REPO_ROOT))
    issues: list[dict] = []
    text = read(path)

    if path.parent.name == "Lenses":
        sections = set(_sections(text))
        for required in LENS_REQUIRED_SECTIONS:
            if required not in sections:
                issues.append(
                    _issue("error", rel, f"lens missing required section `## {required.title()}`")
                )
        cap = _env_cap("LEXICON_LENS_CAP", DEFAULT_LENS_CAP)
        n_lines = len(text.splitlines())
        if n_lines > cap:
            issues.append(
                _issue(
                    "error",
                    rel,
                    f"{n_lines} lines exceeds lens cap of {cap} (LEXICON_LENS_CAP)",
                )
            )
        return issues

    current = None
    for line in unfenced_lines(text):
        if line.startswith("## "):
            name = line[3:].strip()
            current = name.lower()
            if current not in DIRECTION_ALLOWED_SECTIONS:
                issues.append(
                    _issue(
                        "error",
                        rel,
                        f"section `## {name}` not allowed — only Purpose, Principles and "
                        "Standards. Horizon-bound intent belongs in Objectives.md; runnable "
                        "protocols in Direction/Lenses/",
                    )
                )
            continue
        if current in ("principles", "standards") and TOP_BULLET_RE.match(line.strip()):
            if not DIRECTION_ITEM_RE.match(line.strip()):
                issues.append(
                    _issue(
                        "error",
                        rel,
                        f"item `{line.strip()[:60]}…` — principles/standards are one line, "
                        "ID'd and dated: `- P1 — <one line> (adopted YYYY-MM-DD — [[source]])`",
                    )
                )

    cap = _env_cap("LEXICON_DIRECTION_CAP", DEFAULT_DIRECTION_CAP)
    n_lines = len(text.splitlines())
    if n_lines > cap:
        issues.append(
            _issue(
                "error",
                rel,
                f"{n_lines} lines exceeds direction cap of {cap} (LEXICON_DIRECTION_CAP) — "
                "operational detail belongs in docs/ and rules; promoting at cap means retiring",
            )
        )
    if not fm_date(frontmatter_block(text), "direction_updated"):
        issues.append(_issue("warning", rel, "no `direction_updated:` date in frontmatter"))
    return issues


# ------------------------------------------------------------- Objectives ----

def known_direction_areas() -> list[str]:
    direction = REPO_ROOT / "Direction"
    if not direction.is_dir():
        return []
    return sorted(
        p.stem for p in direction.glob("*.md") if p.stem.lower() not in ("readme", "index")
    )


def lint_objectives() -> list[dict]:
    """Cap, WIG, required fields, area link, and Evidence-path existence."""
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
            _issue(
                "error",
                rel,
                f"{len(objectives)} active objectives exceeds cap of {cap} — "
                "retire one before opening another",
            )
        )

    wigs = sum(1 for obj in objectives if obj["wig"])
    if wigs != 1:
        issues.append(_issue("error", rel, f"expected exactly one [WIG], found {wigs}"))

    areas = set(known_direction_areas())
    today = date.today().isoformat()

    for obj in objectives:
        title = obj["title"]
        for key in obj["missing_fields"]:
            issues.append(
                _issue("error", rel, f"`{title}`: missing **{OBJECTIVE_FIELD_LABELS[key]}:**")
            )
        if obj["area"] and areas and obj["area"] not in areas:
            issues.append(
                _issue(
                    "error",
                    rel,
                    f"`{title}`: area `{obj['area']}` has no Direction/{obj['area']}.md",
                )
            )
        for ev_path in obj["evidence"]:
            if not (REPO_ROOT / ev_path).exists():
                issues.append(
                    _issue(
                        "error",
                        rel,
                        f"`{title}`: Evidence path `{ev_path}` does not exist — "
                        "a dead path makes the review's evidence step silently empty",
                    )
                )
        if obj["by"] and obj["by"] < today:
            issues.append(
                _issue(
                    "warning",
                    rel,
                    f"`{title}`: past its due date ({obj['by']}) and still active — "
                    "retire it or reopen with a new date in review",
                )
            )

    return issues


# ------------------------------------------------------------------ Sweep ----

def lint_structure() -> list[dict]:
    """Vault-level checks: un-migrated legacy roots, areas missing files."""
    issues: list[dict] = []
    for name in LEGACY_ROOTS:
        p = REPO_ROOT / name
        if p.is_dir() and any(f.suffix == ".md" and not _skippable(f) for f in p.rglob("*.md")):
            issues.append(
                _issue(
                    "warning",
                    name,
                    f"legacy top-level `{name}/` still holds content — migrate to the "
                    "tier directories (docs/UPDATING.md)",
                )
            )

    evidence = REPO_ROOT / "Evidence"
    areas = set(known_direction_areas())
    if evidence.is_dir():
        for area_dir in sorted(p for p in evidence.iterdir() if p.is_dir()):
            if not (REPO_ROOT / "Synthesis" / f"{area_dir.name}.md").is_file():
                issues.append(
                    _issue(
                        "warning",
                        str(area_dir.relative_to(REPO_ROOT)),
                        f"area has evidence but no Synthesis/{area_dir.name}.md — "
                        "first triage creates it",
                    )
                )
            if areas and area_dir.name not in areas:
                issues.append(
                    _issue(
                        "warning",
                        str(area_dir.relative_to(REPO_ROOT)),
                        f"area has no Direction/{area_dir.name}.md",
                    )
                )
    return issues


# ---------------------------------------------------------------- Routing ----

def lint_path(path: Path) -> list[dict]:
    """Route one file to its tier checker by path — the write-time gate."""
    try:
        rel = path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return [_issue("error", str(path), "outside the vault")]
    if _skippable(path):
        return []
    top = rel.parts[0] if rel.parts else ""
    if top == "Sources":
        return lint_source_file(REPO_ROOT / rel)
    if top == "Evidence":
        return lint_evidence_file(REPO_ROOT / rel)
    if top == "Synthesis":
        return lint_synthesis_file(REPO_ROOT / rel)
    if top == "Direction":
        return lint_direction_file(REPO_ROOT / rel)
    if str(rel) == "Objectives.md":
        return lint_objectives()
    return []


def _area_of(rel: Path) -> str | None:
    parts = rel.parts
    if parts[0] in ("Evidence",) and len(parts) > 2:
        return parts[1]
    if parts[0] == "Sources" and len(parts) > 3:
        return parts[2]
    if parts[0] == "Synthesis" and len(parts) >= 2:
        return Path(parts[1]).stem
    return None


def _sweep(roots: list[str], area: str | None) -> list[dict]:
    issues: list[dict] = []
    for root in roots:
        base = REPO_ROOT / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if _skippable(path):
                continue
            rel = path.relative_to(REPO_ROOT)
            if area:
                file_area = _area_of(rel)
                if file_area is not None and file_area.lower() != area.lower():
                    continue
            issues.extend(lint_path(path))
    return issues


def lint_capture_files(area: str | None = None) -> list[dict]:
    """Every capture file under Sources/ through the tier checker."""
    return _sweep(list(CAPTURE_ROOTS), area)


def lint_direction() -> list[dict]:
    """Every Direction/ file (lenses included) through the tier checker."""
    return _sweep(["Direction"], None)


def lint_all(area: str | None) -> list[dict]:
    issues = _sweep(list(CAPTURE_ROOTS) + ["Evidence", "Synthesis", "Direction"], area)
    issues.extend(lint_objectives())
    issues.extend(lint_structure())
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint Lexicon vault hygiene")
    parser.add_argument("--area", dest="area", help="Limit to one area slug")
    parser.add_argument("--project", dest="area", help=argparse.SUPPRESS)  # deprecated alias
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="PATH",
        help="Lint only these files (the write-time gate every writer runs)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.files:
        issues = []
        for f in args.files:
            issues.extend(lint_path(Path(f)))
    else:
        issues = lint_all(args.area)

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
