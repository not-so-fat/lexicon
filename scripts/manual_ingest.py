#!/usr/bin/env python3
"""
Ingest manual meeting transcript into Lexicon.

Output: Transcripts/Manual/YYYY-MM-DD_<slug>_manual.md (project is in frontmatter only; folder is not project-based).

No external HiNotes (or other) dependency: stub mode is source-agnostic. Full mode optionally parses
HiNotes-style input (Unknown Speaker → HH:MM:SS → paragraph); if you use another format, use --stub and paste into the file.

Modes:
  1. Stub: Create file with metadata only; you fill transcript later.
     python scripts/manual_ingest.py --stub --date YYYY-MM-DD --title "Title" --with-whom "Name" --project personal

  2. Full: Parse HiNotes-format transcript from file or stdin and write formatted file.
     python scripts/manual_ingest.py --date YYYY-MM-DD --with-whom "Name" --project personal [--transcript-file PATH]
     HiNotes format: "Unknown Speaker" → HH:MM:SS → paragraph, repeated.
"""
import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
MANUAL_BASE = os.path.join(REPO_ROOT, "Transcripts", "Manual")

TIMESTAMP_RE = re.compile(r"^\d{1,2}:\d{2}:\d{2}$")


def clean_filename(text):
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "_", text).strip().strip("_") or "meeting"


def parse_hinotes_transcript(raw_text):
    lines = raw_text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "Unknown Speaker":
            i += 1
            ts = ""
            if i < len(lines) and TIMESTAMP_RE.match(lines[i].strip()):
                ts = lines[i].strip()
                i += 1
            para_lines = []
            while i < len(lines):
                if lines[i].strip() == "Unknown Speaker":
                    break
                para_lines.append(lines[i])
                i += 1
            text = "\n".join(para_lines).strip()
            if text:
                blocks.append((ts, text))
            continue
        i += 1
    return blocks


def format_transcript_body(blocks):
    out = []
    for ts, text in blocks:
        if ts:
            out.append(f"**Unknown Speaker ({ts}):** {text}")
        else:
            out.append(f"**Unknown Speaker:** {text}")
    return "\n".join(out)


def create_stub(date_str, title, with_whom, project, out_path):
    safe_title = title.replace('"', '\\"')
    content = f"""---
title: "{safe_title}"
date: {date_str}
with_whom: {with_whom}
project: {project}
source: manual
tags: [transcript, manual, raw, meeting]
---

# Raw Transcript

(Paste or type your transcript here.)
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Ingest manual transcript into Transcripts/Manual/. Project is stored in frontmatter only."
    )
    parser.add_argument("--date", default=None, help="Meeting date YYYY-MM-DD (optional with --stub: default today)")
    parser.add_argument("--title", default=None, help="Meeting title (required for --stub)")
    parser.add_argument("--with-whom", required=True, dest="with_whom", help="With whom (e.g. Satish)")
    parser.add_argument("--project", required=True, help="Project: personal, company, career, general, etc.")
    parser.add_argument("--stub", action="store_true", help="Create stub only; you fill transcript later.")
    parser.add_argument("--transcript-file", dest="transcript_file", default=None, help="Transcript file; default: stdin")
    parser.add_argument("--dry-run", action="store_true", help="Print target path only; do not write")
    args = parser.parse_args()

    from datetime import date as date_module
    date_str = (args.date or "").strip()
    if args.stub and not date_str:
        date_str = date_module.today().strftime("%Y-%m-%d")
    if not args.stub and not date_str:
        print("ERROR: --date required when not using --stub", file=sys.stderr)
        sys.exit(1)
    with_whom = args.with_whom.strip()
    project = args.project.strip()
    title = (args.title or "").strip()
    if not title:
        title = f"Catch up {with_whom}" if args.stub else f"{date_str} {with_whom}"

    slug = clean_filename(title) if args.title else clean_filename(with_whom)
    out_filename = f"{date_str}_{slug}_manual.md"
    out_path = os.path.join(MANUAL_BASE, out_filename)

    if args.stub:
        if args.dry_run:
            print(f"Would write stub: {out_path}")
            return
        os.makedirs(MANUAL_BASE, exist_ok=True)
        create_stub(date_str, title, with_whom, project, out_path)
        print(f"SAVED (stub): {out_path}")
        print("Fill the transcript under # Raw Transcript, then ask the agent to summarize.")
        return

    if args.transcript_file:
        with open(args.transcript_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    else:
        raw_text = sys.stdin.read()

    blocks = parse_hinotes_transcript(raw_text)
    if not blocks:
        print("WARNING: No transcript blocks parsed. Check format (Unknown Speaker / HH:MM:SS / paragraph).", file=sys.stderr)

    if args.dry_run:
        print(f"Would write: {out_path}")
        print(f"Parsed blocks: {len(blocks)}")
        return

    os.makedirs(MANUAL_BASE, exist_ok=True)
    body = format_transcript_body(blocks)
    content = f"""---
title: "{title}"
date: {date_str}
with_whom: {with_whom}
project: {project}
source: manual
tags: [transcript, manual, raw, meeting]
---

# Raw Transcript

{body}
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SAVED: {out_path}")
    print(f"Parsed blocks: {len(blocks)}")
    print("Ask the agent to summarize this transcript, then review before distilling.")


if __name__ == "__main__":
    main()
