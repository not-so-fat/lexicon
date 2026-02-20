#!/usr/bin/env python3
"""
Fetch Fireflies transcripts for a date and account. Saves to Transcripts/Fireflies/<account>/.

Usage:
  python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>
  python scripts/fireflies_collection.py fetch <transcript_id> <account>

Required .env per account: FIREFLIES_API_KEY_<account>, EMAIL_<account>. See .env.example.

Dedup: One transcript per logical meeting (same title + 15-min time bucket). When multiple
recordings exist, we keep the one where organizer_email == EMAIL_<account>; otherwise the
first. If we already have a file for that meeting but with a different transcript ID, we
replace it (upgrade to our recording). Meetings under 5 minutes are skipped.
"""
import os
import sys
import re
import glob
import requests
from datetime import datetime

# --- CONFIGURATION ---
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


def get_config(account):
    """Env: FIREFLIES_API_KEY_<account>, EMAIL_<account>; optional OUTPUT_DIR_<account>."""
    key = account.lower()
    output_dir = os.getenv(f"OUTPUT_DIR_{key}")
    if not output_dir:
        output_dir = os.path.join(REPO_ROOT, "Transcripts", "Fireflies", key)
    project = (os.getenv(f"PROJECT_{key}") or "").strip()
    return {
        "api_key": (os.getenv(f"FIREFLIES_API_KEY_{key}") or "").strip(),
        "email": (os.getenv(f"EMAIL_{key}") or "").strip(),
        "output_dir": output_dir,
        "name": key,
        "project": project,
    }


def validate_config(config, account):
    """Check required .env variables for this account. Exit with a friendly message if something is missing."""
    key = config["name"]
    missing = []
    if not config["api_key"]:
        missing.append(f"FIREFLIES_API_KEY_{key}")
    if not config["email"]:
        missing.append(f"EMAIL_{key}")

    if not missing:
        return

    env_path = os.path.join(REPO_ROOT, ".env")
    print("Configuration error for account '{}':".format(account), file=sys.stderr)
    print("  Missing or empty in .env: " + ", ".join(missing), file=sys.stderr)
    if not os.path.isfile(env_path):
        print("  No .env file found. Copy .env.example to .env and fill in the values.", file=sys.stderr)
    else:
        print("  Add these to your .env (see .env.example for the format):", file=sys.stderr)
        for var in missing:
            print("    {}=<your-value>".format(var), file=sys.stderr)
    print("  Then run again.", file=sys.stderr)
    sys.exit(1)


URL = "https://api.fireflies.ai/graphql"


def run_query(query, config, variables=None):
    if not config["api_key"]:
        validate_config(config, config["name"])
    headers = {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}
    try:
        response = requests.post(URL, json={"query": query, "variables": variables}, headers=headers)
        body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        if not response.ok:
            err = body.get("errors", body) or response.text
            print("API request failed ({} {}).".format(response.status_code, response.reason), file=sys.stderr)
            print(err, file=sys.stderr)
            if response.status_code in (401, 403):
                print("Check that FIREFLIES_API_KEY_{} in .env is correct and not expired.".format(config["name"]), file=sys.stderr)
            sys.exit(1)
        return body.get("data", {})
    except requests.exceptions.RequestException as e:
        print(f"FATAL: API request failed. {e}", file=sys.stderr)
        sys.exit(1)


def clean_filename(text):
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    return re.sub(r'[\\/*?:"<>|]', "", text).strip().replace(" ", "_")


def get_target_filename(m_date_ms, title, m_id, output_dir):
    dt_obj = datetime.fromtimestamp(m_date_ms / 1000)
    date_dash = dt_obj.strftime("%Y-%m-%d")
    safe_title = clean_filename(title)
    return os.path.join(output_dir, f"{date_dash}_{safe_title}_{m_id}.md")


def get_date_title_pattern(m_date_ms, title, output_dir):
    dt_obj = datetime.fromtimestamp(m_date_ms / 1000)
    date_dash = dt_obj.strftime("%Y-%m-%d")
    safe_title = clean_filename(title)
    return os.path.join(output_dir, f"{date_dash}_{safe_title}_*.md")


def fetch_and_save(meeting_id, config):
    query = """
    query GetTranscript($id: String!) {
      transcript(id: $id) {
        id, title, date, participants, transcript_url
        sentences { speaker_name, text }
      }
    }
    """
    data = run_query(query, config, {"id": meeting_id})
    m = data.get("transcript")
    if not m:
        return None
    filename = get_target_filename(m["date"], m["title"], m["id"], config["output_dir"])
    if os.path.exists(filename):
        return ("EXISTING", filename)

    participants_str = "\n".join([f"  - {p}" for p in (m.get("participants") or [])])
    sentences = m.get("sentences") or []
    transcript_str = "\n".join([f"{s.get('speaker_name', '')}: {s.get('text', '')}" for s in sentences])
    meta_date = datetime.fromtimestamp(m["date"] / 1000).strftime("%Y/%m/%d")

    project_line = f"project: {config['project']}\n" if config.get("project") else ""
    content = f"""---
title: {m['title']}
date: {meta_date}
{project_line}participants:
{participants_str}
meeting_link: {m['transcript_url']}
fireflies_id: {m['id']}
source: Fireflies
tags: [transcript, fireflies, meeting]
---

# Raw Transcript

{transcript_str}
"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return ("SAVED", filename)


def parse_date(date_str):
    """Return datetime for date_str. Exit with friendly error if format is wrong."""
    if not date_str or not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str.strip()):
        print("Invalid date. Use YYYY-MM-DD (e.g. 2026-02-17).", file=sys.stderr)
        sys.exit(1)
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        print("Invalid date '{}'. Use YYYY-MM-DD (e.g. 2026-02-17).".format(date_str), file=sys.stderr)
        sys.exit(1)


def dedup_transcripts(transcripts, priority_email, min_duration_min=5, time_bucket_ms=15 * 60 * 1000):
    """
    One transcript per logical meeting (same title + same 15-min time bucket).
    Prefer the recording where organizer_email == priority_email; else first in group.
    Returns (chosen_transcripts, ignored_short_descriptions).
    """
    ignored = []
    grouped = {}
    for t in transcripts:
        if t.get("duration") is not None and t["duration"] < min_duration_min:
            ignored.append(f"{t['title']} ({t['duration']} min)")
            continue
        bucket = (t["date"] // time_bucket_ms) * time_bucket_ms
        key = (t["title"], bucket)
        grouped.setdefault(key, []).append(t)
    chosen = [
        next((m for m in meetings if m.get("organizer_email") == priority_email), meetings[0])
        for meetings in grouped.values()
    ]
    return chosen, ignored


def process_date(date_str, config):
    """Fetch all transcripts for the given date; one file per logical meeting (dedup by title + 15min bucket)."""
    dt = parse_date(date_str)
    date_str = dt.strftime("%Y-%m-%d")
    print(f"--- Processing {date_str} for account '{config['name']}' ---")
    from_date = dt.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    to_date = dt.replace(hour=23, minute=59, second=59, microsecond=999000).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    query = """
    query GetTranscripts($fromDate: DateTime, $toDate: DateTime) {
      transcripts(fromDate: $fromDate, toDate: $toDate) {
        id, title, date, organizer_email, duration, transcript_url
      }
    }
    """
    data = run_query(query, config, {"fromDate": from_date, "toDate": to_date})
    transcripts = data.get("transcripts", [])

    chosen, ignored_short = dedup_transcripts(transcripts, config["email"])
    summary = {"saved": [], "skipped": [], "ignored_short": ignored_short, "replaced": []}

    for target in chosen:
        pattern = get_date_title_pattern(target["date"], target["title"], config["output_dir"])
        existing_files = glob.glob(pattern)
        if existing_files:
            existing_path = existing_files[0]
            existing_id = os.path.basename(existing_path).replace(".md", "").split("_")[-1]
            if existing_id == target["id"]:
                summary["skipped"].append(existing_path)
                continue
            os.remove(existing_path)
            summary["replaced"].append(existing_path)
        result = fetch_and_save(target["id"], config)
        if result:
            kind, path = result
            if kind == "EXISTING":
                summary["skipped"].append(path)
            else:
                summary["saved"].append(path)

    print(f"\nRESULTS for {date_str}:")
    print(f"  - New files saved: {len(summary['saved'])}")
    for s in summary["saved"]:
        print(f"    {s}")
    if summary["replaced"]:
        print(f"  - Replaced (upgraded to priority recording): {len(summary['replaced'])}")
        for r in summary["replaced"]:
            print(f"    {r}")
    print(f"  - Already exists: {len(summary['skipped'])}")
    print(f"  - Ignored (short): {len(summary['ignored_short'])}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    val = sys.argv[2] if len(sys.argv) > 2 else None
    account = (sys.argv[3] if len(sys.argv) > 3 else "personal").lower()
    config = get_config(account)
    validate_config(config, account)
    if mode == "process-date":
        if not val:
            print("Usage: python scripts/fireflies_collection.py process-date YYYY-MM-DD <account>", file=sys.stderr)
            print("Example: python scripts/fireflies_collection.py process-date 2026-02-17 personal", file=sys.stderr)
            sys.exit(1)
        process_date(val, config)
    elif mode == "fetch":
        if not val:
            print("Usage: python scripts/fireflies_collection.py fetch <transcript_id> <account>", file=sys.stderr)
            sys.exit(1)
        result = fetch_and_save(val, config)
        if result:
            kind, path = result
            print(f"{kind}: {path}")
    else:
        print("Usage: process-date YYYY-MM-DD <account>  |  fetch <transcript_id> <account>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
