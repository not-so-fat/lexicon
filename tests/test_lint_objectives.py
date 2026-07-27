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


def test_leftover_lexicon_processing_strategy_is_a_warning(vault, monkeypatch):
    """git checkout does not delete files the template removed — this leftover
    is the deleted `Memory/Lexicon/processing-strategy.md`, which contradicts
    `Direction/Lexicon.md` and sits under a path lint never otherwise scans."""
    (vault / "Memory" / "Lexicon").mkdir(parents=True)
    (vault / "Memory" / "Lexicon" / "processing-strategy.md").write_text(
        "# old charter", encoding="utf-8"
    )

    issues = _issues(vault, monkeypatch, "lint_direction")

    assert any(
        i["level"] == "warning" and "Direction/Lexicon.md" in i["issue"]
        for i in issues
        if i["path"] == "Memory/Lexicon/processing-strategy.md"
    )


def test_no_leftover_lexicon_charter_warning_when_file_absent(vault, monkeypatch):
    issues = _issues(vault, monkeypatch, "lint_direction")

    assert not any(
        i["path"] == "Memory/Lexicon/processing-strategy.md" for i in issues
    )


def test_empty_objectives_file_produces_no_issues(vault, write_objectives, monkeypatch):
    write_objectives("")

    issues = _issues(vault, monkeypatch, "lint_objectives")

    assert issues == []


def test_disallowed_section_inside_fence_is_not_an_error(vault, monkeypatch):
    (vault / "Direction" / "kite.md").write_text(
        "---\narea: kite\n---\n\n# Direction — Kite\n\n"
        "## Purpose\n\nx\n\n"
        "## Standards\n\n"
        "Example of what not to write:\n\n"
        "```markdown\n## Objectives\n\nnope\n```\n",
        encoding="utf-8",
    )

    issues = _issues(vault, monkeypatch, "lint_direction")

    assert issues == []


def test_disallowed_section_outside_fence_still_errors(vault, monkeypatch):
    (vault / "Direction" / "kite.md").write_text(
        "---\narea: kite\n---\n\n# Direction — Kite\n\n"
        "## Purpose\n\nx\n\n## Objectives\n\nnope\n",
        encoding="utf-8",
    )

    issues = _issues(vault, monkeypatch, "lint_direction")

    assert any(
        i["level"] == "error" and "Objectives" in i["issue"] for i in issues
    )


def test_fenced_section_ignored_but_real_disallowed_section_caught(vault, monkeypatch):
    (vault / "Direction" / "kite.md").write_text(
        "---\narea: kite\n---\n\n# Direction — Kite\n\n"
        "## Purpose\n\nx\n\n"
        "Example of what not to write:\n\n"
        "```markdown\n## Objectives\n\nnope\n```\n\n"
        "## Roadmap\n\nreal offender\n",
        encoding="utf-8",
    )

    issues = _issues(vault, monkeypatch, "lint_direction")

    offenders = [i["issue"] for i in issues if i["level"] == "error"]
    assert not any("section `## Objectives`" in msg for msg in offenders)
    assert any("section `## Roadmap`" in msg for msg in offenders)


def test_inner_fence_marker_with_info_string_does_not_close_outer_fence(vault, monkeypatch):
    """A fence-shaped line with trailing text (an info string) inside an
    already-open fence must not be treated as the close — CommonMark requires
    a closing fence line to contain nothing but the marker and whitespace.
    Without that check, a worked example nested inside a worked example
    (outer fence containing text that itself shows a fenced snippet) would
    prematurely "close" on the inner opening marker, re-enabling the section
    whitelist partway through content that is still fenced.
    """
    (vault / "Direction" / "kite.md").write_text(
        "---\narea: kite\n---\n\n# Direction — Kite\n\n"
        "## Purpose\n\nx\n\n"
        "## Standards\n\n"
        "Example of an example inside an example:\n\n"
        "```markdown\n"
        "Some text\n\n"
        "```python\n"
        "## Objectives\n\n"
        "nope\n"
        "```\n"
        "```\n",
        encoding="utf-8",
    )

    issues = _issues(vault, monkeypatch, "lint_direction")

    offenders = [i["issue"] for i in issues if i["level"] == "error"]
    assert not any("section `## Objectives`" in msg for msg in offenders)
