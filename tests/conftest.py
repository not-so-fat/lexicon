"""Fixtures building a throwaway vault so tests never touch the real one."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """Minimal vault: one area with a direction file and one evidence log."""
    (tmp_path / "Direction").mkdir()
    (tmp_path / "Direction" / "acme.md").write_text(
        "---\narea: acme\ndirection_updated: 2026-07-01\n---\n\n"
        "# Direction — Acme\n\n"
        "## Purpose\n\nWhy this area exists.\n\n"
        "## Principles\n\nA standing constraint.\n\n"
        "## Standards\n\nA quality bar.\n",
        encoding="utf-8",
    )
    (tmp_path / "Memory" / "acme").mkdir(parents=True)
    (tmp_path / "Memory" / "acme" / "Product.evidence.md").write_text(
        "# Evidence (append-only)\n"
        "- 2026-07-10 — a thing happened — Source: [[Some Meeting]]\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def write_objectives(vault: Path):
    """Write Objectives.md with the given `## Active` body."""

    def _write(body: str, reviewed: str = "2026-07-20") -> Path:
        path = vault / "Objectives.md"
        path.write_text(
            "---\n"
            "cycle: 2026-Q3\n"
            "objectives_updated: 2026-07-20\n"
            f"reviewed: {reviewed}\n"
            "---\n\n"
            "# Objectives — cycle 2026-Q3\n\n"
            "## Active\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        return path

    return _write
