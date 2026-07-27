#!/usr/bin/env python3
"""
Rewrite legacy `project:` frontmatter to `area:` across a vault.

The old key still works everywhere (readers fall back to it permanently --
see docs/superpowers/specs/2026-07-27-terminology-clarity-design.md D6),
so this script is a convenience, not a requirement. It exists because
`lint_vault.py` warns on the old key, and running it once clears the debt.

Only rewrites the frontmatter KEY. Never touches the word "project" in
prose, titles, or body text -- that word still means something else
(an H1 deliverable) and rewriting it would be wrong, not merely unhelpful.

Usage:
  python3 scripts/migrate_area_key.py [root] [--dry-run] [--json]

Exit 0 always (this is not a linter). Prints the files it changed (or
would change, under --dry-run).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FRONTMATTER_RE = re.compile(r"^(---\s*\n)(.*?)(\n---)", re.DOTALL)
# A frontmatter line whose key is exactly `project`, scalar or list-headed.
PROJECT_KEY_RE = re.compile(r"^project:(.*)$", re.MULTILINE)
AREA_KEY_PRESENT_RE = re.compile(r"^area:\s*\S", re.MULTILINE)


def rewrite_frontmatter_key(text: str) -> tuple[str, bool]:
    """Rewrite `project:` to `area:` inside the frontmatter block only.

    Returns (possibly-rewritten text, whether a change was made). If
    `area:` is already present, the file is left untouched -- migrating
    would either clobber a deliberately different value or duplicate
    the key, and neither is this script's call to make silently.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return text, False

    fm_body = match.group(2)
    if AREA_KEY_PRESENT_RE.search(fm_body):
        return text, False
    if not PROJECT_KEY_RE.search(fm_body):
        return text, False

    new_fm_body = PROJECT_KEY_RE.sub(r"area:\1", fm_body, count=1)
    new_text = text[: match.start(2)] + new_fm_body + text[match.end(2) :]
    return new_text, True


def migrate_tree(root: Path, dry_run: bool) -> list[Path]:
    changed: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        new_text, did_change = rewrite_frontmatter_key(text)
        if did_change:
            changed.append(path)
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(REPO_ROOT), help="Directory to sweep (default: repo root)")
    parser.add_argument("--dry-run", action="store_true", help="Report only; do not write")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    changed = migrate_tree(root, dry_run=args.dry_run)
    rel_changed = [str(p.relative_to(root)) for p in changed]

    if args.json:
        print(json.dumps({"changed": rel_changed, "dry_run": args.dry_run}, indent=2))
    else:
        verb = "Would change" if args.dry_run else "Changed"
        print(f"{verb} {len(rel_changed)} file(s).")
        for p in rel_changed:
            print(f"  {p}")

    sys.exit(0)


if __name__ == "__main__":
    main()
