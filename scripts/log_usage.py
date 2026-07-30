#!/usr/bin/env python3
"""
Append vault-file accesses to Metadata/usage/access.jsonl — the capture side of
the usage QA layer (docs/MEMORY_MODEL.md). Deterministic by design: a hook
records reads so telemetry never depends on an agent remembering to log.

Hook mode (default) — wire as a Claude Code PostToolUse hook for Read/Grep/Glob:

  // .claude/settings.json (or ~/.claude/settings.json with an absolute path)
  {
    "hooks": {
      "PostToolUse": [
        {
          "matcher": "Read|Grep|Glob",
          "hooks": [{"type": "command",
                     "command": "python3 scripts/log_usage.py"}]
        }
      ]
    }
  }

Reads the hook's JSON payload from stdin, extracts any path inside the vault,
appends one JSONL line per file. Always exits 0 — telemetry must never block a
session.

Manual mode — for agents/hosts without hooks (best-effort fallback):

  python3 scripts/log_usage.py --paths Synthesis/kite.md Evidence/kite/Product.md --tool manual

Log line: {"ts": ISO8601, "path": vault-relative, "tool": str, "session": str}
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.resolve()
LOG_DIR = REPO_ROOT / "Metadata" / "usage"
LOG_FILE = LOG_DIR / "access.jsonl"

TRACKED_TOPS = {"Sources", "Evidence", "Synthesis", "Direction"}
TRACKED_FILES = {"Objectives.md", "Objectives.evidence.md"}


def vault_relative(raw: str) -> str | None:
    """Vault-relative path if `raw` points at a tracked vault file, else None."""
    if not raw or not isinstance(raw, str):
        return None
    try:
        p = Path(raw)
        if not p.is_absolute():
            p = REPO_ROOT / p
        rel = p.resolve().relative_to(REPO_ROOT)
    except (ValueError, OSError):
        return None
    rel_s = str(rel)
    if rel_s in TRACKED_FILES:
        return rel_s
    if rel.parts and rel.parts[0] in TRACKED_TOPS and rel_s.endswith(".md"):
        return rel_s
    return None


def paths_from_hook_payload(payload: dict) -> set[str]:
    """Every tracked vault path mentioned anywhere in tool_input/tool_response."""
    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str):
            rel = vault_relative(node)
            if rel:
                found.add(rel)

    if "tool_input" in payload or "tool_response" in payload:
        # Claude Code PostToolUse shape.
        walk(payload.get("tool_input", {}))
        # Grep/Glob results name the files that were actually read/matched.
        walk(payload.get("tool_response"))
    else:
        # Other hosts (e.g. Cursor hooks) use different keys — scan everything.
        walk(payload)
    return found


def append(paths: set[str], tool: str, session: str) -> None:
    if not paths:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        for path in sorted(paths):
            f.write(
                json.dumps(
                    {"ts": ts, "path": path, "tool": tool, "session": session},
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Log vault-file accesses")
    parser.add_argument("--paths", nargs="+", help="Manual mode: paths that were read")
    parser.add_argument("--tool", default="manual", help="Manual mode: tool label")
    parser.add_argument("--session", default="", help="Manual mode: session label")
    args = parser.parse_args()

    try:
        if args.paths:
            paths = {rel for raw in args.paths if (rel := vault_relative(raw))}
            append(paths, args.tool, args.session)
        else:
            payload = json.load(sys.stdin)
            paths = paths_from_hook_payload(payload)
            append(
                paths,
                str(payload.get("tool_name", "unknown")),
                str(payload.get("session_id", "")),
            )
    except Exception:
        pass  # telemetry must never block the session
    sys.exit(0)


if __name__ == "__main__":
    main()
