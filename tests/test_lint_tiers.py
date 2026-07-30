"""Tier-contract checks: Evidence / Synthesis / Direction / decision files,
the --files routing, and the synthesis-status side of triage_queue."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lint_vault
import triage_queue


@pytest.fixture
def tier_vault(tmp_path: Path) -> Path:
    (tmp_path / "Direction" / "Lenses").mkdir(parents=True)
    (tmp_path / "Evidence" / "acme").mkdir(parents=True)
    (tmp_path / "Synthesis" / "acme" / "decisions").mkdir(parents=True)
    (tmp_path / "Direction" / "acme.md").write_text(
        "---\narea: acme\ndirection_updated: 2026-07-01\n---\n# Direction — Acme\n"
        "## Purpose\np\n"
        "## Principles\n- P1 — one line (adopted 2026-07-01)\n"
        "## Standards\n- S1 — a bar (adopted 2026-07-01 — [[x]])\n",
        encoding="utf-8",
    )
    (tmp_path / "Evidence" / "acme" / "Product.md").write_text(
        "# Evidence (append-only)\n- 2026-07-10 — good — Source: [[X]]\n",
        encoding="utf-8",
    )
    (tmp_path / "Synthesis" / "acme.md").write_text(
        "---\narea: acme\nsynthesized: 2026-07-20\n---\n# Current synthesis\nok\n",
        encoding="utf-8",
    )
    return tmp_path


def _lint(vault, monkeypatch, path):
    monkeypatch.setattr(lint_vault, "REPO_ROOT", vault)
    return lint_vault.lint_path(vault / path)


def test_clean_tier_vault_lints_clean(tier_vault, monkeypatch):
    monkeypatch.setattr(lint_vault, "REPO_ROOT", tier_vault)
    assert lint_vault.lint_all(None) == []


def test_undated_bullet_orphan_and_prose_are_errors(tier_vault, monkeypatch):
    (tier_vault / "Evidence" / "acme" / "Product.md").write_text(
        "# Evidence (append-only)\n"
        "- undated bullet\n"
        "  - orphaned sub-bullet\n"
        "stray prose\n",
        encoding="utf-8",
    )
    issues = _lint(tier_vault, monkeypatch, "Evidence/acme/Product.md")
    msgs = " | ".join(i["issue"] for i in issues if i["level"] == "error")
    assert "not dated" in msgs
    assert "orphaned sub-bullet" in msgs
    assert "undated block" in msgs


def test_oversized_bullet_is_an_error(tier_vault, monkeypatch):
    (tier_vault / "Evidence" / "acme" / "Product.md").write_text(
        "# Evidence (append-only)\n- 2026-07-10 — " + "x" * 260 + "\n",
        encoding="utf-8",
    )
    issues = _lint(tier_vault, monkeypatch, "Evidence/acme/Product.md")
    assert any("chars" in i["issue"] for i in issues if i["level"] == "error")


def test_synthesis_needs_stamp_and_respects_cap(tier_vault, monkeypatch):
    (tier_vault / "Synthesis" / "acme.md").write_text(
        "---\narea: acme\n---\n# Current synthesis\n" + "line\n" * 130,
        encoding="utf-8",
    )
    issues = _lint(tier_vault, monkeypatch, "Synthesis/acme.md")
    msgs = " | ".join(i["issue"] for i in issues if i["level"] == "error")
    assert "synthesized" in msgs
    assert "exceeds synthesis cap" in msgs


def test_synthesis_disallowed_section_is_an_error(tier_vault, monkeypatch):
    (tier_vault / "Synthesis" / "acme.md").write_text(
        "---\narea: acme\nsynthesized: 2026-07-20\n---\n# Current synthesis\nok\n\n## Roadmap\n",
        encoding="utf-8",
    )
    issues = _lint(tier_vault, monkeypatch, "Synthesis/acme.md")
    assert any("## roadmap" in i["issue"].lower() for i in issues if i["level"] == "error")


def test_decision_file_contract(tier_vault, monkeypatch):
    bad = tier_vault / "Synthesis" / "acme" / "decisions" / "bet.md"
    bad.write_text(
        "---\narea: acme\nopened: 2026-07-01\nstatus: wat\n---\n# Bet\n## Frame\n- x\n",
        encoding="utf-8",
    )
    issues = _lint(tier_vault, monkeypatch, "Synthesis/acme/decisions/bet.md")
    msgs = " | ".join(i["issue"] for i in issues if i["level"] == "error")
    assert "decide-by" in msgs
    assert "status" in msgs
    assert "Acceptance test" in msgs

    bad.write_text(
        "---\narea: acme\nopened: 2026-07-01\ndecide-by: 2026-08-15\nstatus: open\n---\n"
        "# Bet\n## Frame\n- x\n## Acceptance test\n- 2026-07-20 — buyer shares it\n",
        encoding="utf-8",
    )
    assert _lint(tier_vault, monkeypatch, "Synthesis/acme/decisions/bet.md") == []


def test_direction_item_shape_is_enforced(tier_vault, monkeypatch):
    (tier_vault / "Direction" / "acme.md").write_text(
        "---\narea: acme\ndirection_updated: 2026-07-01\n---\n# D\n"
        "## Purpose\np\n## Principles\n- an unshaped item\n## Standards\n",
        encoding="utf-8",
    )
    issues = _lint(tier_vault, monkeypatch, "Direction/acme.md")
    assert any("ID'd and dated" in i["issue"] for i in issues if i["level"] == "error")


def test_lens_required_sections_and_cap(tier_vault, monkeypatch):
    lens = tier_vault / "Direction" / "Lenses" / "foo.md"
    lens.write_text("# Lens\n## Process\nsteps\n", encoding="utf-8")
    issues = _lint(tier_vault, monkeypatch, "Direction/Lenses/foo.md")
    msgs = " | ".join(i["issue"] for i in issues)
    assert "When To Run This" in msgs
    assert "Failure-Mode Guards" in msgs

    lens.write_text(
        "# Lens\n## When to run this\nt\n## Process\nsteps\n## Failure-mode guards\ng\n",
        encoding="utf-8",
    )
    assert _lint(tier_vault, monkeypatch, "Direction/Lenses/foo.md") == []


def test_dead_objective_evidence_path_is_an_error(tier_vault, monkeypatch):
    (tier_vault / "Objectives.md").write_text(
        "---\ncycle: 2026-Q3\n---\n## Active\n\n"
        "### [WIG] Ship\n- **Area:** acme\n- **By:** 2099-01-01\n"
        "- **Done when:** d\n- **Obstacle:** o\n"
        "- **Evidence:** Evidence/acme/NOPE.md\n- **Opened:** 2026-07-01\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(lint_vault, "REPO_ROOT", tier_vault)
    issues = lint_vault.lint_objectives()
    assert any("does not exist" in i["issue"] for i in issues if i["level"] == "error")


def test_synthesis_status_staleness_and_pending_promotion(tier_vault, monkeypatch):
    monkeypatch.setattr(triage_queue, "REPO_ROOT", tier_vault)
    (tier_vault / "Evidence" / "acme" / "Product.md").write_text(
        "# Evidence (append-only)\n"
        "- 2026-07-10 — drained already — Source: [[X]]\n"
        "- 2026-08-30 — new fact — Source: [[Y]]\n"
        "- 2026-08-30 — Pending decision: pick a partner — Source: [[Y]]\n",
        encoding="utf-8",
    )
    status = triage_queue.synthesis_status("acme")
    assert status["synthesized"] == "2026-07-20"
    assert status["newest_evidence"] == "2026-08-30"
    assert status["stale"] is True
    assert status["new_evidence"][0]["new_bullets"] == 2
    assert any("pick a partner" in p for p in status["pending_decision_bullets"])


def test_overdue_decision_is_flagged(tier_vault, monkeypatch):
    monkeypatch.setattr(triage_queue, "REPO_ROOT", tier_vault)
    (tier_vault / "Synthesis" / "acme" / "decisions" / "bet.md").write_text(
        "---\narea: acme\nopened: 2026-06-01\ndecide-by: 2026-07-01\nstatus: open\n---\n# Bet\n",
        encoding="utf-8",
    )
    decisions = triage_queue.open_decisions("acme", today="2026-07-29")
    assert decisions[0]["overdue"] is True


def test_pending_entity_proposals_parsed(tier_vault, monkeypatch):
    monkeypatch.setattr(triage_queue, "REPO_ROOT", tier_vault)
    (tier_vault / "Metadata").mkdir()
    (tier_vault / "Metadata" / "entity_registry.md").write_text(
        "# Entity registry\n\n## Canonical\n\n- **Ada Lovelace** (person) — aliases: Ada Loveless\n\n"
        "## Proposed (review at triage)\n\n"
        "- 2026-07-29 — **Chi Chang** (person?) — likely alias of **Chi Zhang**; heard in [[X]]\n",
        encoding="utf-8",
    )
    proposals = triage_queue.pending_entity_proposals()
    assert len(proposals) == 1 and "Chi Chang" in proposals[0]


def test_synthesis_people_and_partner_reads_are_tolerated(tier_vault, monkeypatch):
    (tier_vault / "Synthesis" / "acme" / "people").mkdir()
    (tier_vault / "Synthesis" / "acme" / "partners").mkdir()
    (tier_vault / "Synthesis" / "acme" / "people" / "Ada.md").write_text(
        "# Ada\nfree-form current read, any shape\n", encoding="utf-8"
    )
    (tier_vault / "Synthesis" / "acme" / "partners" / "AcmeCorp.md").write_text(
        "# AcmeCorp\npartner model prose\n", encoding="utf-8"
    )
    assert _lint(tier_vault, monkeypatch, "Synthesis/acme/people/Ada.md") == []
    assert _lint(tier_vault, monkeypatch, "Synthesis/acme/partners/AcmeCorp.md") == []
