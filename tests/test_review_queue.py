from datetime import date

import review_queue

ONE_WIG = """### [WIG] Decide the platform migration
- **Area:** acme
- **Horizon:** 2026-08-30
- **Done when:** a written go/no-go call exists
- **Obstacle:** the deadline passes and nobody decides
- **Evidence:** Memory/acme/Product.evidence.md
- **Opened:** 2026-07-26
"""

TWO_OBJECTIVES = ONE_WIG + """
### Resolve the vendor evaluation
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
    assert obj["title"] == "Decide the platform migration"
    assert obj["area"] == "acme"
    assert obj["horizon"] == "2026-08-30"
    assert obj["opened"] == "2026-07-26"
    assert obj["evidence"] == ["Memory/acme/Product.evidence.md"]
    assert obj["missing_fields"] == []


def test_parses_multiple_and_marks_non_wig(write_objectives):
    path = write_objectives(TWO_OBJECTIVES)
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert [o["title"] for o in objectives] == [
        "Decide the platform migration",
        "Resolve the vendor evaluation",
    ]
    assert [o["wig"] for o in objectives] == [True, False]


def test_reports_missing_required_fields(write_objectives):
    path = write_objectives(
        "### Half-written objective\n"
        "- **Area:** acme\n"
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
        ONE_WIG + "\n## Notes\n\n### Not an objective\n- **Area:** acme\n"
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert len(objectives) == 1


def test_splits_multiple_evidence_paths(write_objectives):
    path = write_objectives(
        ONE_WIG.replace(
            "- **Evidence:** Memory/acme/Product.evidence.md",
            "- **Evidence:** Memory/acme/Product.evidence.md, Meetings/acme",
        )
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert objectives[0]["evidence"] == [
        "Memory/acme/Product.evidence.md",
        "Meetings/acme",
    ]


def test_commented_out_example_is_not_parsed_as_an_objective(write_objectives):
    path = write_objectives(
        "<!--\n"
        "### [WIG] <outcome, not activity>\n"
        "- **Area:** <area — must match a Direction/<area>.md>\n"
        "- **Horizon:** YYYY-MM-DD\n"
        "- **Done when:** <observable recognition condition — not a metric>\n"
        "- **Obstacle:** <the thing most likely to prevent it>\n"
        "- **Evidence:** <comma-separated vault paths the review reads>\n"
        "- **Opened:** YYYY-MM-DD\n"
        "-->\n"
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert objectives == []


def test_real_objective_after_a_commented_example_is_still_parsed(write_objectives):
    path = write_objectives(
        "<!--\n"
        "### [WIG] <outcome, not activity>\n"
        "- **Area:** <area — must match a Direction/<area>.md>\n"
        "-->\n"
        "\n" + ONE_WIG
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert len(objectives) == 1
    assert objectives[0]["title"] == "Decide the platform migration"
    assert objectives[0]["area"] == "acme"


def test_fenced_wig_example_is_not_parsed_as_a_live_objective(write_objectives):
    """docs/OBJECTIVES.md presents the objective schema inside a ```markdown
    fence — copying that shape verbatim as a worked example under `## Active`
    must not add a second, phantom [WIG]."""
    path = write_objectives(
        ONE_WIG
        + "\n"
        "Example of the shape:\n\n"
        "```markdown\n"
        "### [WIG] <outcome, not activity>\n"
        "- **Area:** <area>\n"
        "- **Horizon:** YYYY-MM-DD\n"
        "- **Done when:** <condition>\n"
        "- **Obstacle:** <thing>\n"
        "- **Evidence:** <paths>\n"
        "- **Opened:** YYYY-MM-DD\n"
        "```\n"
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert len(objectives) == 1
    assert objectives[0]["title"] == "Decide the platform migration"
    assert sum(1 for o in objectives if o["wig"]) == 1


def test_fenced_heading_does_not_terminate_the_scan(write_objectives):
    """A fenced `## Something` line must not be mistaken for the end of
    `## Active` — the un-fence-aware scanner used to `break` on it and drop
    every objective that followed, silently defeating the cap check."""
    path = write_objectives(
        ONE_WIG
        + "\n"
        "```markdown\n"
        "## Something that looks like a section break\n"
        "```\n\n"
        "### Resolve the vendor evaluation\n"
        "- **Area:** personal\n"
        "- **Horizon:** 2026-09-30\n"
        "- **Done when:** an offer exists to weigh, or both tracks are closed in writing\n"
        "- **Obstacle:** the sprint absorbs every week\n"
        "- **Evidence:** Memory/personal\n"
        "- **Opened:** 2026-07-26\n"
    )
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert [o["title"] for o in objectives] == [
        "Decide the platform migration",
        "Resolve the vendor evaluation",
    ]


def test_shipped_objectives_scaffold_has_no_live_objectives():
    """Regression: the committed root Objectives.md is a scaffold with a
    commented-out example only. It must parse as zero active objectives —
    this is the exact bug a comment-blind parser would miss."""
    path = review_queue.REPO_ROOT / "Objectives.md"
    objectives = review_queue.parse_objectives(path.read_text(encoding="utf-8"))

    assert objectives == []


def test_newest_evidence_reads_dated_bullets_in_a_file(vault):
    assert (
        review_queue.newest_evidence_date(vault, ["Memory/acme/Product.evidence.md"])
        == "2026-07-10"
    )


def test_newest_evidence_reads_dated_filenames_in_a_directory(vault):
    meetings = vault / "Meetings" / "acme"
    meetings.mkdir(parents=True)
    (meetings / "2026-07-15 Some Meeting.md").write_text("x", encoding="utf-8")
    (meetings / "2026-06-01 Older Meeting.md").write_text("x", encoding="utf-8")

    assert review_queue.newest_evidence_date(vault, ["Meetings/acme"]) == "2026-07-15"


def test_newest_evidence_takes_the_max_across_paths(vault):
    meetings = vault / "Meetings" / "acme"
    meetings.mkdir(parents=True)
    (meetings / "2026-07-22 Later.md").write_text("x", encoding="utf-8")

    assert (
        review_queue.newest_evidence_date(
            vault, ["Memory/acme/Product.evidence.md", "Meetings/acme"]
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

    assert review_queue.known_areas(vault) == ["acme", "personal"]


def test_known_areas_excludes_the_lexicon_charter(vault):
    """Direction/Lexicon.md is the tool's own charter, not a user area."""
    (vault / "Direction" / "Lexicon.md").write_text("# Direction", encoding="utf-8")

    assert review_queue.known_areas(vault) == ["acme"]


def test_report_flags_cap_breach_and_wig_count(write_objectives, vault, monkeypatch):
    monkeypatch.setenv("LEXICON_OBJECTIVE_CAP", "2")
    body = ""
    for i in range(3):
        body += (
            f"### Objective {i}\n"
            "- **Area:** acme\n"
            "- **Horizon:** 2026-12-31\n"
            "- **Done when:** something observable\n"
            "- **Obstacle:** something likely\n"
            "- **Evidence:** Memory/acme/Product.evidence.md\n"
            "- **Opened:** 2026-07-01\n\n"
        )
    write_objectives(body)

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["active_count"] == 3
    assert report["cap"] == 2
    assert report["cap_breach"] is True
    assert report["wig_count"] == 0


def test_days_between_returns_none_on_malformed_date():
    """A typo'd evidence bullet date (e.g. `2026-13-45`, month 13) must not
    crash the queue — `DATED_BULLET_RE` matches the digit shape without
    validating the calendar value."""
    assert review_queue._days_between("2026-13-45", date(2026, 7, 27)) is None


def test_report_survives_a_malformed_evidence_date(write_objectives, vault):
    (vault / "Memory" / "acme" / "Product.evidence.md").write_text(
        "# Evidence (append-only)\n"
        "- 2026-07-10 — a thing happened — Source: [[Some Meeting]]\n"
        "- 2026-13-45 — a typo'd date — Source: [[Some Meeting]]\n",
        encoding="utf-8",
    )
    write_objectives(ONE_WIG)

    report = review_queue.build_report(vault, date(2026, 7, 27))
    obj = report["objectives"][0]

    assert obj["newest_evidence"] == "2026-13-45"
    assert obj["days_since_evidence"] is None


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

    assert report["past_horizon"] == ["Decide the platform migration"]
    assert report["objectives"][0]["days_to_horizon"] == -26


def test_report_lists_areas_governed_only_by_standards(write_objectives, vault):
    (vault / "Direction" / "research.md").write_text("# Direction", encoding="utf-8")
    write_objectives(ONE_WIG)

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["areas_without_objectives"] == ["research"]


def test_report_flags_stale_review(write_objectives, vault):
    write_objectives(ONE_WIG, reviewed="2026-07-01")

    report = review_queue.build_report(vault, date(2026, 7, 27))

    assert report["days_since_review"] == 26
    assert report["review_stale"] is True


def test_render_labels_zero_objective_areas_as_governed_by_standards(
    write_objectives, vault
):
    (vault / "Direction" / "research.md").write_text("# Direction", encoding="utf-8")
    write_objectives(ONE_WIG)

    text = review_queue.render(review_queue.build_report(vault, date(2026, 7, 27)))

    assert "research" in text
    assert "governed by Standards" in text
    assert "WARN" not in text


def test_render_flags_cap_breach_and_missing_wig(write_objectives, vault, monkeypatch):
    monkeypatch.setenv("LEXICON_OBJECTIVE_CAP", "1")
    write_objectives(ONE_WIG.replace("[WIG] ", "") + "\n" + ONE_WIG.replace(
        "Decide the platform migration", "Another objective"
    ).replace("[WIG] ", ""))

    text = review_queue.render(review_queue.build_report(vault, date(2026, 7, 27)))

    assert "exceeds cap" in text
    assert "no [WIG]" in text


def test_render_never_emits_a_score(write_objectives, vault):
    write_objectives(ONE_WIG)

    text = review_queue.render(review_queue.build_report(vault, date(2026, 7, 27)))

    for banned in ("score", "%", "moving", "stalled", "drifting"):
        assert banned not in text.lower()
