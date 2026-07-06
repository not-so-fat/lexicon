#!/usr/bin/env python3
"""
Run hinotes_organizer from Lexicon (USB sync + transcribe → Transcripts/HiDock/).

Requires hinotes_organizer configured with output.dir pointing at this vault's Transcripts/HiDock/.

Usage:
  python scripts/hidock_collection.py run [--limit N]

Environment:
  HIDOCK_ORGANIZER_ROOT  Path to hinotes_organizer repo (required)
  HIDOCK_CONFIG          Optional path to config.yaml (default: <organizer>/config.yaml)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")

env_path = os.path.join(REPO_ROOT, ".env")
if os.path.isfile(env_path):
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _resolve_organizer_root() -> str:
    root = (os.getenv("HIDOCK_ORGANIZER_ROOT") or "").strip()
    if not root:
        print(
            "Configuration error: set HIDOCK_ORGANIZER_ROOT in .env to your hinotes_organizer checkout.",
            file=sys.stderr,
        )
        sys.exit(1)
    root = os.path.expanduser(root)
    if not os.path.isdir(root):
        print(f"HIDOCK_ORGANIZER_ROOT is not a directory: {root}", file=sys.stderr)
        sys.exit(1)
    return root


def _python_for_organizer(organizer_root: str) -> str:
    venv_python = os.path.join(organizer_root, ".venv", "bin", "python")
    if os.path.isfile(venv_python):
        return venv_python
    return sys.executable


def run_pipeline(limit: int | None = None) -> int:
    organizer_root = _resolve_organizer_root()
    pipeline = os.path.join(organizer_root, "scripts", "pipeline.py")
    if not os.path.isfile(pipeline):
        print(f"Missing {pipeline}. Check HIDOCK_ORGANIZER_ROOT.", file=sys.stderr)
        sys.exit(1)

    config = (os.getenv("HIDOCK_CONFIG") or "").strip()
    if not config:
        config = os.path.join(organizer_root, "config.yaml")
    if not os.path.isfile(config):
        print(f"Missing config: {config}", file=sys.stderr)
        print("Copy config.example.yaml to config.yaml in hinotes_organizer.", file=sys.stderr)
        sys.exit(1)

    hidock_out = os.path.join(REPO_ROOT, "Transcripts", "HiDock")
    os.makedirs(hidock_out, exist_ok=True)

    cmd = [
        _python_for_organizer(organizer_root),
        pipeline,
        "--config",
        config,
        "run",
    ]
    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    print(f"Running hinotes_organizer from {organizer_root}", file=sys.stderr)
    result = subprocess.run(cmd, cwd=organizer_root)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch HiDock transcripts via hinotes_organizer")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="Sync device and transcribe new recordings")
    run_p.add_argument("--limit", type=int, default=None, help="Max files per phase (testing)")
    args = parser.parse_args()

    if args.command == "run":
        sys.exit(run_pipeline(limit=args.limit))


if __name__ == "__main__":
    main()
