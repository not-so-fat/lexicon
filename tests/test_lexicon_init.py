from pathlib import Path

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
    """The shipped root files are the spec — a scaffolded vault must be identical."""
    lexicon_init.scaffold_objectives(tmp_path)

    for name in ("Objectives.md", "Objectives.evidence.md"):
        assert (tmp_path / name).read_bytes() == (REPO_ROOT / name).read_bytes()
