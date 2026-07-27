import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SCRIPTS_DIR = SCRIPTS
sys.path.insert(0, str(SCRIPTS))

import triage_queue as tq


def test_area_matches_reads_new_key():
    fm = {"area": "acme"}
    assert tq.area_matches(fm, None, "acme") is True
    assert tq.area_matches(fm, None, "other") is False


def test_area_matches_falls_back_to_project_key():
    fm = {"project": "acme"}
    assert tq.area_matches(fm, None, "acme") is True


def test_area_matches_prefers_area_over_project_when_both_present():
    fm = {"area": "acme", "project": "personal"}
    assert tq.area_matches(fm, None, "acme") is True
    assert tq.area_matches(fm, None, "personal") is False


def test_area_matches_handles_list_value():
    fm = {"area": ["acme"]}
    assert tq.area_matches(fm, None, "acme") is True


def test_area_matches_falls_back_to_folder_when_no_frontmatter_key():
    fm = {}
    assert tq.area_matches(fm, "acme", "acme") is True
    assert tq.area_matches(fm, "other", "acme") is False


def test_build_queue_parameter_is_named_area(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tq, "REPO_ROOT", tmp_path)
    ideas = tmp_path / "Ideas" / "acme"
    ideas.mkdir(parents=True)
    (ideas / "2026-07-01 Idea.md").write_text(
        "---\narea: acme\ncreated: 2026-07-01\n---\n\n# Idea\n", encoding="utf-8"
    )
    queue = tq.build_queue(area="acme", since=None, until=None)
    assert len(queue) == 1
    assert queue[0]["path"].endswith("2026-07-01 Idea.md")


def test_build_queue_finds_legacy_project_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tq, "REPO_ROOT", tmp_path)
    ideas = tmp_path / "Ideas" / "acme"
    ideas.mkdir(parents=True)
    (ideas / "2026-07-01 Idea.md").write_text(
        "---\nproject: acme\ncreated: 2026-07-01\n---\n\n# Idea\n", encoding="utf-8"
    )
    queue = tq.build_queue(area="acme", since=None, until=None)
    assert len(queue) == 1


def test_area_flag_works(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "triage_queue.py"), "--area", "nosuchvault"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "nosuchvault" in result.stdout


def test_deprecated_project_flag_still_works(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "triage_queue.py"), "--project", "nosuchvault"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "nosuchvault" in result.stdout


def test_missing_area_and_project_errors(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "triage_queue.py")],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode != 0
