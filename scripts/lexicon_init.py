#!/usr/bin/env python3
"""
Create Lexicon folder skeleton if missing. Sync primary user from .env to Metadata/User.md. Remind to set .env.

Usage: python scripts/lexicon_init.py

Run from repo root. Safe to run multiple times.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")

DIRS = [
    "Transcripts",
    "Transcripts/Fireflies",
    "Transcripts/Manual",
    "Meetings",
    "People",
    "Memory",
    "Metadata",
]


def _load_env(root):
    env_path = os.path.join(root, ".env")
    if not os.path.isfile(env_path):
        return
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


def main():
    root = REPO_ROOT
    for d in DIRS:
        path = os.path.join(root, d)
        os.makedirs(path, exist_ok=True)
        print(f"  {path}")
    print("\nFolders OK.")

    _load_env(root)
    user_name = (os.getenv("LEXICON_USER_NAME") or "").strip()
    if user_name:
        metadata_dir = os.path.join(root, "Metadata")
        user_md = os.path.join(metadata_dir, "User.md")
        content = f"Primary user: {user_name}\n"
        with open(user_md, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Synced LEXICON_USER_NAME to {user_md}")

    env = os.path.join(root, ".env")
    if not os.path.isfile(env):
        print("Copy .env.example to .env and set FIREFLIES_API_KEY_<account>, EMAIL_<account> (default account: personal), and optionally LEXICON_USER_NAME.")
    else:
        print(".env present. Run process-date via the agent or: python scripts/fireflies_collection.py process-date YYYY-MM-DD <account> (e.g. personal)")


if __name__ == "__main__":
    main()
