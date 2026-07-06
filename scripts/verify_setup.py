#!/usr/bin/env python3
"""
Check Lexicon installation and optional source connectors.

Usage:
  python scripts/verify_setup.py

Exit 0 if required checks pass; 1 if any required check fails.
HiDock and Fireflies are optional — reported as warnings when not configured.
"""
from __future__ import annotations

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
ENV_PATH = os.path.join(REPO_ROOT, ".env")
HIDOCK_OUT = os.path.join(REPO_ROOT, "Transcripts", "HiDock")

REQUIRED_DIRS = [
    "Transcripts/Fireflies",
    "Transcripts/HiDock",
    "Transcripts/Manual",
    "Meetings",
    "People",
    "Memory",
    "Ideas",
    "Metadata",
]

OUTPUT_DIR_RE = re.compile(r"^\s*dir:\s*(.+?)\s*(?:#.*)?$")
ASSEMBLYAI_KEY_RE = re.compile(r"^\s*assemblyai_api_key:\s*['\"]?(\S*)['\"]?\s*(?:#.*)?$")


def _load_env() -> None:
    if not os.path.isfile(ENV_PATH):
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _ok(msg: str) -> None:
    print(f"  OK  {msg}")


def _warn(msg: str) -> None:
    print(f"  --  {msg}")


def _fail(msg: str) -> None:
    print(f"  !!  {msg}", file=sys.stderr)


def _read_output_dir(config_path: str, organizer_root: str) -> str | None:
    try:
        text = open(config_path, encoding="utf-8").read()
    except OSError:
        return None

    in_output = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("output:"):
            in_output = True
            continue
        if in_output:
            if stripped and not line.startswith((" ", "\t")) and not stripped.startswith("#"):
                break
            match = OUTPUT_DIR_RE.match(line)
            if match:
                raw = match.group(1).strip().strip('"').strip("'")
                path = os.path.expanduser(raw)
                if not os.path.isabs(path):
                    path = os.path.join(organizer_root, path)
                return os.path.realpath(path)
    return None


def _has_assemblyai_key(config_path: str) -> bool:
    try:
        text = open(config_path, encoding="utf-8").read()
    except OSError:
        return False
    for line in text.splitlines():
        match = ASSEMBLYAI_KEY_RE.match(line)
        if match and match.group(1).strip():
            return True
    return False


def check_core() -> bool:
    print("Lexicon core")
    ok = True

    for rel in REQUIRED_DIRS:
        path = os.path.join(REPO_ROOT, rel)
        if os.path.isdir(path):
            _ok(rel)
        else:
            _fail(f"Missing folder: {rel} (run python scripts/lexicon_init.py)")
            ok = False

    if not os.path.isfile(ENV_PATH):
        _fail("No .env — copy .env.example to .env and fill in values")
        return False
    _ok(".env present")

    user = (os.getenv("LEXICON_USER_NAME") or "").strip()
    if user:
        _ok(f"LEXICON_USER_NAME set ({user})")
    else:
        _fail("LEXICON_USER_NAME empty — needed for AI Evaluation in meeting notes")
        ok = False

    return ok


def check_fireflies() -> None:
    print("\nFireflies (optional)")
    accounts = []
    for key, value in os.environ.items():
        if key.startswith("FIREFLIES_API_KEY_") and value.strip():
            accounts.append(key.removeprefix("FIREFLIES_API_KEY_"))

    if not accounts:
        _warn("Not configured — skip if you only use HiDock or manual transcripts")
        return

    for account in accounts:
        api = os.getenv(f"FIREFLIES_API_KEY_{account}", "").strip()
        email = os.getenv(f"EMAIL_{account}", "").strip()
        if api and email:
            _ok(f"account '{account}' (API key + email)")
        elif api:
            _warn(f"account '{account}': missing EMAIL_{account}")
        else:
            _warn(f"account '{account}': missing API key")


def check_hidock() -> None:
    print("\nHiDock (optional)")
    root = (os.getenv("HIDOCK_ORGANIZER_ROOT") or "").strip()
    if not root:
        _warn("HIDOCK_ORGANIZER_ROOT not set — skip if you do not use HiDock")
        _warn("See docs/SETUP.md § HiDock")
        return

    root = os.path.realpath(os.path.expanduser(root))
    if not os.path.isdir(root):
        _fail(f"HIDOCK_ORGANIZER_ROOT not found: {root}")
        return
    _ok(f"organizer repo: {root}")

    pipeline = os.path.join(root, "scripts", "pipeline.py")
    if os.path.isfile(pipeline):
        _ok("pipeline.py found")
    else:
        _fail(f"Missing {pipeline}")
        return

    config = (os.getenv("HIDOCK_CONFIG") or "").strip()
    if not config:
        config = os.path.join(root, "config.yaml")
    else:
        config = os.path.expanduser(config)

    if not os.path.isfile(config):
        _fail(f"Missing config: {config} (cp config.example.yaml config.yaml in hinotes_organizer)")
        return
    _ok(f"config: {config}")

    expected_out = os.path.realpath(HIDOCK_OUT)
    actual_out = _read_output_dir(config, root)
    if actual_out is None:
        _fail("Could not read output.dir from hinotes_organizer config")
    elif actual_out == expected_out:
        _ok(f"output.dir → Transcripts/HiDock/")
    else:
        _fail("output.dir mismatch")
        print(f"       expected: {expected_out}", file=sys.stderr)
        print(f"       config:   {actual_out}", file=sys.stderr)
        print("       Set output.dir in hinotes_organizer config.yaml (see docs/SETUP.md)", file=sys.stderr)

    if _has_assemblyai_key(config):
        _ok("assemblyai_api_key set in organizer config")
    else:
        _warn("assemblyai_api_key missing in organizer config (required for default cloud transcribe)")

    venv_py = os.path.join(root, ".venv", "bin", "python")
    if os.path.isfile(venv_py):
        _ok("hinotes_organizer .venv present")
    else:
        _warn("No .venv in hinotes_organizer — run ./scripts/setup.sh there first")


def main() -> None:
    _load_env()
    print(f"Repo: {REPO_ROOT}\n")

    core_ok = check_core()
    check_fireflies()
    check_hidock()

    print()
    if core_ok:
        print("Core setup OK. Optional sources above — fix any !! before using HiDock/Fireflies.")
        sys.exit(0)

    print("Fix required issues above, then re-run: python scripts/verify_setup.py", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
