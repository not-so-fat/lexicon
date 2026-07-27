from pathlib import Path

import lexicon_init


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
