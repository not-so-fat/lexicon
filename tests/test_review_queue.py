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
