from datetime import date

import review_queue

ONE_WIG = """### [WIG] Decide the Circle hinge
- **Area:** kite
- **Horizon:** 2026-08-30
- **Done when:** a written stay-or-go call exists
- **Obstacle:** the bonus decides it by default
- **Evidence:** Memory/kite/Product.evidence.md
- **Opened:** 2026-07-26
"""

TWO_OBJECTIVES = ONE_WIG + """
### Resolve the external track
- **Area:** personal
- **Horizon:** 2026-09-30
- **Done when:** an offer exists to weigh, or both tracks are closed in writing
- **Obstacle:** the sprint absorbs every week
- **Evidence:** Memory/personal
- **Opened:** 2026-07-26
"""


def test_parses_wig_flag_and_fields(write_objectives):
    path = write_objectives(ONE_WIG)
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert len(objectives) == 1
    obj = objectives[0]
    assert obj["wig"] is True
    assert obj["title"] == "Decide the Circle hinge"
    assert obj["area"] == "kite"
    assert obj["horizon"] == "2026-08-30"
    assert obj["opened"] == "2026-07-26"
    assert obj["evidence"] == ["Memory/kite/Product.evidence.md"]
    assert obj["missing_fields"] == []


def test_parses_multiple_and_marks_non_wig(write_objectives):
    path = write_objectives(TWO_OBJECTIVES)
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert [o["title"] for o in objectives] == [
        "Decide the Circle hinge",
        "Resolve the external track",
    ]
    assert [o["wig"] for o in objectives] == [True, False]


def test_reports_missing_required_fields(write_objectives):
    path = write_objectives(
        "### Half-written objective\n"
        "- **Area:** kite\n"
        "- **Opened:** 2026-07-26\n"
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert objectives[0]["missing_fields"] == [
        "horizon",
        "done when",
        "obstacle",
        "evidence",
    ]


def test_ignores_content_after_active_section(write_objectives):
    path = write_objectives(
        ONE_WIG + "\n## Notes\n\n### Not an objective\n- **Area:** kite\n"
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert len(objectives) == 1


def test_splits_multiple_evidence_paths(write_objectives):
    path = write_objectives(
        ONE_WIG.replace(
            "- **Evidence:** Memory/kite/Product.evidence.md",
            "- **Evidence:** Memory/kite/Product.evidence.md, Meetings/kite",
        )
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert objectives[0]["evidence"] == [
        "Memory/kite/Product.evidence.md",
        "Meetings/kite",
    ]


def test_newest_evidence_reads_dated_bullets_in_a_file(vault):
    assert (
        review_queue.newest_evidence_date(vault, ["Memory/kite/Product.evidence.md"])
        == "2026-07-10"
    )


def test_newest_evidence_reads_dated_filenames_in_a_directory(vault):
    meetings = vault / "Meetings" / "kite"
    meetings.mkdir(parents=True)
    (meetings / "2026-07-15 Some Meeting.md").write_text("x", encoding="utf-8")
    (meetings / "2026-06-01 Older Meeting.md").write_text("x", encoding="utf-8")

    assert review_queue.newest_evidence_date(vault, ["Meetings/kite"]) == "2026-07-15"


def test_newest_evidence_takes_the_max_across_paths(vault):
    meetings = vault / "Meetings" / "kite"
    meetings.mkdir(parents=True)
    (meetings / "2026-07-22 Later.md").write_text("x", encoding="utf-8")

    assert (
        review_queue.newest_evidence_date(
            vault, ["Memory/kite/Product.evidence.md", "Meetings/kite"]
        )
        == "2026-07-22"
    )


def test_newest_evidence_ignores_missing_paths(vault):
    assert review_queue.newest_evidence_date(vault, ["Nope/does-not-exist.md"]) == ""


def test_last_review_picks_the_newest_iso_week_file(vault):
    review_dir = vault / "Metadata" / "review"
    review_dir.mkdir(parents=True)
    (review_dir / "2026-W28.md").write_text("x", encoding="utf-8")
    (review_dir / "2026-W30.md").write_text("x", encoding="utf-8")

    iso_date, relpath = review_queue.last_review(vault)

    assert iso_date == "2026-07-20"  # Monday of ISO week 2026-W30
    assert relpath == "Metadata/review/2026-W30.md"


def test_last_review_empty_when_no_review_dir(vault):
    assert review_queue.last_review(vault) == ("", "")


def test_known_areas_from_direction_files(vault):
    (vault / "Direction" / "personal.md").write_text("# Direction", encoding="utf-8")
    (vault / "Direction" / "README.md").write_text("# Readme", encoding="utf-8")

    assert review_queue.known_areas(vault) == ["kite", "personal"]


def test_known_areas_excludes_the_lexicon_charter(vault):
    """Direction/Lexicon.md is the tool's own charter, not a user area."""
    (vault / "Direction" / "Lexicon.md").write_text("# Direction", encoding="utf-8")

    assert review_queue.known_areas(vault) == ["kite"]


def test_report_flags_cap_breach_and_wig_count(write_objectives, vault, monkeypatch):
    monkeypatch.setenv("LEXICON_OBJECTIVE_CAP", "2")
    body = ""
    for i in range(3):
        body += (
            f"### Objective {i}\n"
            "- **Area:** kite\n"
            "- **Horizon:** 2026-12-31\n"
            "- **Done when:** something observable\n"
            "- **Obstacle:** something likely\n"
            "- **Evidence:** Memory/kite/Product.evidence.md\n"
            "- **Opened:** 2026-07-01\n\n"
        )
    write_objectives(body)

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["active_count"] == 3
    assert report["cap"] == 2
    assert report["cap_breach"] is True
    assert report["wig_count"] == 0


def test_report_computes_horizon_and_evidence_staleness(write_objectives, vault):
    write_objectives(ONE_WIG)

    report = review_queue.build_report(vault, date(2026, 7, 27))
    obj = report["objectives"][0]

    assert obj["days_to_horizon"] == 34
    assert obj["past_horizon"] is False
    assert obj["newest_evidence"] == "2026-07-10"
    assert obj["days_since_evidence"] == 17


def test_report_flags_past_horizon_and_soon(write_objectives, vault):
    write_objectives(ONE_WIG.replace("2026-08-30", "2026-07-01"))

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["past_horizon"] == ["Decide the Circle hinge"]
    assert report["objectives"][0]["days_to_horizon"] == -26


def test_report_lists_areas_governed_only_by_standards(write_objectives, vault):
    (vault / "Direction" / "aaron.md").write_text("# Direction", encoding="utf-8")
    write_objectives(ONE_WIG)

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["areas_without_objectives"] == ["aaron"]


def test_report_flags_stale_review(write_objectives, vault):
    write_objectives(ONE_WIG, reviewed="2026-07-01")

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["days_since_review"] == 26
    assert report["review_stale"] is True


def test_render_labels_zero_objective_areas_as_governed_by_standards(
    write_objectives, vault
):
    (vault / "Direction" / "aaron.md").write_text("# Direction", encoding="utf-8")
    write_objectives(ONE_WIG)

    text = review_queue.render(review_queue.build_report(vault, date(2026, 7, 27)))

    assert "aaron" in text
    assert "governed by Standards" in text
    assert "WARN" not in text


def test_render_flags_cap_breach_and_missing_wig(write_objectives, vault, monkeypatch):
    monkeypatch.setenv("LEXICON_OBJECTIVE_CAP", "1")
    write_objectives(ONE_WIG.replace("[WIG] ", "") + "\n" + ONE_WIG.replace(
        "Decide the Circle hinge", "Another objective"
    ).replace("[WIG] ", ""))

    text = review_queue.render(review_queue.build_report(vault, date(2026, 7, 27)))

    assert "exceeds cap" in text
    assert "no [WIG]" in text


def test_render_never_emits_a_score(write_objectives, vault):
    write_objectives(ONE_WIG)

    text = review_queue.render(review_queue.build_report(vault, date(2026, 7, 27)))

    for banned in ("score", "%", "moving", "stalled", "drifting"):
        assert banned not in text.lower()
