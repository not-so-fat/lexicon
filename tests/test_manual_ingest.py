import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "manual_ingest.py"), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_area_flag_writes_area_key(tmp_path, monkeypatch):
    result = run(
        ["--stub", "--date", "2026-07-01", "--title", "Test", "--with-whom", "Alex", "--area", "acme"],
        cwd=tmp_path,
    )
    assert result.returncode == 0
    stub = next(tmp_path.glob("Transcripts/Manual/*.md"))
    text = stub.read_text(encoding="utf-8")
    assert "area: acme" in text
    assert "project:" not in text


def test_deprecated_project_flag_still_works(tmp_path):
    result = run(
        ["--stub", "--date", "2026-07-01", "--title", "Test", "--with-whom", "Alex", "--project", "acme"],
        cwd=tmp_path,
    )
    assert result.returncode == 0
    stub = next(tmp_path.glob("Transcripts/Manual/*.md"))
    assert "area: acme" in stub.read_text(encoding="utf-8")


def test_missing_area_and_project_errors(tmp_path):
    result = run(
        ["--stub", "--date", "2026-07-01", "--title", "Test", "--with-whom", "Alex"],
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "--area" in result.stderr
