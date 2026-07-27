import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import migrate_area_key as mak


def test_rewrites_project_key_to_area():
    text = "---\ntitle: X\nproject: acme\ntags: []\n---\n\nBody\n"
    result, changed = mak.rewrite_frontmatter_key(text)
    assert changed is True
    assert "area: acme" in result
    assert "project:" not in result


def test_leaves_file_with_area_key_unchanged():
    text = "---\ntitle: X\narea: acme\n---\n\nBody\n"
    result, changed = mak.rewrite_frontmatter_key(text)
    assert changed is False
    assert result == text


def test_leaves_file_with_no_project_key_unchanged():
    text = "---\ntitle: X\n---\n\nBody\n"
    result, changed = mak.rewrite_frontmatter_key(text)
    assert changed is False


def test_does_not_touch_project_word_in_prose():
    text = "---\ntitle: X\n---\n\nThis project is going well.\n"
    result, changed = mak.rewrite_frontmatter_key(text)
    assert changed is False
    assert "This project is going well." in result


def test_preserves_list_value():
    text = "---\ntitle: X\nproject:\n  - acme\n  - side\n---\n\nBody\n"
    result, changed = mak.rewrite_frontmatter_key(text)
    assert changed is True
    assert "area:\n  - acme\n  - side" in result


def test_both_keys_present_leaves_project_untouched_and_warns_via_return(capsys):
    text = "---\ntitle: X\narea: acme\nproject: old\n---\n\nBody\n"
    result, changed = mak.rewrite_frontmatter_key(text)
    assert changed is False
    assert result == text  # area: already present -- do not clobber it, do not delete project: silently


def test_migrate_tree_dry_run_reports_without_writing(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("---\nproject: acme\n---\n\nBody\n", encoding="utf-8")

    changed = mak.migrate_tree(tmp_path, dry_run=True)

    assert changed == [f]
    assert "project: acme" in f.read_text(encoding="utf-8")  # untouched


def test_migrate_tree_writes_when_not_dry_run(tmp_path):
    f = tmp_path / "note.md"
    f.write_text("---\nproject: acme\n---\n\nBody\n", encoding="utf-8")

    changed = mak.migrate_tree(tmp_path, dry_run=False)

    assert changed == [f]
    assert "area: acme" in f.read_text(encoding="utf-8")


def test_migrate_tree_skips_non_markdown(tmp_path):
    (tmp_path / "note.txt").write_text("project: acme\n", encoding="utf-8")
    changed = mak.migrate_tree(tmp_path, dry_run=False)
    assert changed == []
