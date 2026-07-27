from datetime import date

import lint_vault

GOOD = """### [WIG] Decide the Circle hinge
- **Area:** kite
- **Horizon:** 2026-08-30
- **Done when:** a written stay-or-go call exists
- **Obstacle:** the bonus decides it by default
- **Evidence:** Memory/kite/Product.evidence.md
- **Opened:** 2026-07-26
"""


def _issues(vault, monkeypatch, func_name):
    monkeypatch.setattr(lint_vault, "REPO_ROOT", vault)
    return getattr(lint_vault, func_name)()


def test_clean_objectives_file_produces_no_issues(vault, write_objectives, monkeypatch):
    write_objectives(GOOD)
    assert _issues(vault, monkeypatch, "lint_objectives") == []


def test_cap_breach_is_an_error(vault, write_objectives, monkeypatch):
    monkeypatch.setenv("LEXICON_OBJECTIVE_CAP", "1")
    write_objectives(GOOD + GOOD.replace("[WIG] Decide", "Another"))

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert any(i["level"] == "error" and "exceeds cap" in i["issue"] for i in issues)


def test_missing_wig_is_an_error(vault, write_objectives, monkeypatch):
    write_objectives(GOOD.replace("[WIG] ", ""))

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert any(i["level"] == "error" and "exactly one [WIG]" in i["issue"] for i in issues)


def test_missing_required_field_is_an_error(vault, write_objectives, monkeypatch):
    write_objectives(GOOD.replace("- **Obstacle:** the bonus decides it by default\n", ""))

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert any(i["level"] == "error" and "Obstacle" in i["issue"] for i in issues)


def test_unknown_area_is_an_error(vault, write_objectives, monkeypatch):
    write_objectives(GOOD.replace("- **Area:** kite", "- **Area:** nosucharea"))

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert any(
        i["level"] == "error" and "no Direction/nosucharea.md" in i["issue"] for i in issues
    )


def test_past_horizon_is_a_warning(vault, write_objectives, monkeypatch):
    write_objectives(GOOD.replace("2026-08-30", "2020-01-01"))

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert any(i["level"] == "warning" and "past its Horizon" in i["issue"] for i in issues)


def test_missing_objectives_file_produces_no_issues(vault, monkeypatch):
    assert _issues(vault, monkeypatch, "lint_objectives") == []


def test_disallowed_direction_section_is_an_error(vault, monkeypatch):
    (vault / "Direction" / "kite.md").write_text(
        "---\narea: kite\n---\n\n# Direction — Kite\n\n"
        "## Purpose\n\nx\n\n## Objectives\n\nnope\n",
        encoding="utf-8",
    )

    issues = _issues(vault, monkeypatch, "lint_direction")

    assert any(
        i["level"] == "error" and "Objectives" in i["issue"] for i in issues
    )


def test_leftover_memory_direction_file_is_a_warning(vault, monkeypatch):
    (vault / "Memory" / "kite" / "Direction.md").write_text("# old", encoding="utf-8")

    issues = _issues(vault, monkeypatch, "lint_direction")

    assert any(i["level"] == "warning" and "un-migrated" in i["issue"] for i in issues)


def test_area_without_direction_file_is_a_warning(vault, monkeypatch):
    (vault / "Memory" / "personal").mkdir(parents=True)

    issues = _issues(vault, monkeypatch, "lint_direction")

    assert any(
        i["level"] == "warning" and "Direction/personal.md" in i["issue"] for i in issues
    )


def test_empty_objectives_file_produces_no_issues(vault, write_objectives, monkeypatch):
    write_objectives("")

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert issues == []
