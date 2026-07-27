from pathlib import Path

import pytest

import lexicon_init
import review_queue

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_detect_areas_excludes_lexicon_charter_and_stray_files(vault: Path):
    (vault / "Memory" / "Lexicon").mkdir(parents=True)
    (vault / "Memory" / "notes.md").write_text("stray file", encoding="utf-8")

    assert lexicon_init._detect_areas(vault) == ["kite"]


def test_detect_areas_empty_when_no_memory_dir(tmp_path: Path):
    assert lexicon_init._detect_areas(tmp_path) == []


def test_scaffold_direction_never_overwrites_existing_file(vault: Path):
    existing = (vault / "Direction" / "kite.md").read_text(encoding="utf-8")

    created = lexicon_init.scaffold_direction(vault, ["kite"])

    assert created == []
    assert (vault / "Direction" / "kite.md").read_text(encoding="utf-8") == existing


def test_scaffold_direction_creates_missing_area_and_is_idempotent(vault: Path):
    (vault / "Memory" / "health").mkdir(parents=True)

    created = lexicon_init.scaffold_direction(vault, ["kite", "health"])
    assert [Path(p).name for p in created] == ["health.md"]

    health = (vault / "Direction" / "health.md").read_text(encoding="utf-8")
    assert "area: health" in health
    assert "# Direction — Health" in health

    created_again = lexicon_init.scaffold_direction(vault, ["kite", "health"])
    assert created_again == []


def test_scaffold_objectives_creates_both_files_and_is_idempotent(tmp_path: Path):
    created = lexicon_init.scaffold_objectives(tmp_path)

    assert sorted(Path(p).name for p in created) == [
        "Objectives.evidence.md",
        "Objectives.md",
    ]
    before = {
        name: (tmp_path / name).read_text(encoding="utf-8")
        for name in ("Objectives.md", "Objectives.evidence.md")
    }

    created_again = lexicon_init.scaffold_objectives(tmp_path)

    assert created_again == []
    for name, text in before.items():
        assert (tmp_path / name).read_text(encoding="utf-8") == text


def test_scaffolded_objectives_parse_to_zero_objectives(tmp_path: Path):
    """The commented example is an example, not an objective."""
    lexicon_init.scaffold_objectives(tmp_path)

    text = (tmp_path / "Objectives.md").read_text(encoding="utf-8")

    assert review_queue.parse_objectives(text) == []


def test_objectives_templates_match_the_shipped_files(tmp_path: Path):
    """Catches `OBJECTIVES_TEMPLATE` / `OBJECTIVES_EVIDENCE_TEMPLATE` drifting
    from what the template repo ships at its root — there, the root files
    *are* the untouched scaffold, so byte-identity is the right check.

    Skipped once the root `Objectives.md` has been authored past the scaffold
    (any real vault after its first objective): `tests/` is not in the sync
    list, so a cloned vault carries this test forever, and comparing against
    a legitimately-authored file would fail it on every run rather than
    catching a real desync.
    """
    scaffolded = tmp_path / "scaffold"
    scaffolded.mkdir()
    lexicon_init.scaffold_objectives(scaffolded)

    shipped_objectives = (REPO_ROOT / "Objectives.md").read_bytes()
    if shipped_objectives != (scaffolded / "Objectives.md").read_bytes():
        pytest.skip(
            "repo-root Objectives.md has been authored past the scaffold — "
            "expected in a real vault, nothing to compare"
        )

    for name in ("Objectives.md", "Objectives.evidence.md"):
        assert (scaffolded / name).read_bytes() == (REPO_ROOT / name).read_bytes()
