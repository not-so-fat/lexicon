# Keeping your vault up to date

Your vault starts as a clone of this repo. After that, **your content is yours** — updates only touch the engine.

## Engine vs content

| Engine (synced from template) | Content (never synced — yours) |
|---|---|
| `.cursor/rules/`, `.cursor/skills/`, `.cursor/templates/` | `Meetings/`, `Memory/` (except `Memory/Lexicon/`), `People/`, `Ideas/`, `Transcripts/` |
| `scripts/`, `Memory/Lexicon/`, `Direction/README.md`, `Direction/Lexicon.md` (direction file) | `Metadata/` (registries, recap logs, review logs, `User.md`) |
| `docs/`, `README.md`, `requirements.txt`, `.env.example` | `.env`, `.cursor/rules/local-*.mdc`, `Objectives.md`, `Objectives.evidence.md`, `Direction/<area>.md` |

## Recommended setup (private vault + template upstream)

Keep your vault in your **own private repo** and pull engine updates from the template:

```bash
# once — inside your vault
git remote rename origin template        # if you cloned this repo directly
git remote add origin <your-private-repo-url>
git push -u origin main

# whenever you want updates
git fetch template
git checkout template/main -- .cursor/rules .cursor/skills .cursor/templates scripts docs Memory/Lexicon Direction/Lexicon.md Direction/README.md README.md requirements.txt .env.example
git diff --stat                          # review what changed
# commit to your private repo as usual
```

`git checkout template/main -- <paths>` overwrites only files the template ships. Files that exist only in your vault — `local-*.mdc` rules, extra scripts, all content — are untouched.

**Deletions are not propagated.** `git checkout <tree-ish> -- <path>` copies files that exist in `<tree-ish>`; it has no file to copy for one the template *removed*, so it silently leaves your stale copy in place. This is a general trap, not a one-off — any future template reorg that deletes a file needs an explicit `git rm -f <path>` on your side, because the sync command alone cannot know to remove it. Watch template release notes for removals, or a `lint_vault.py` warning that names the replacement.

## Migrating to the normative tier

The normative tier moved out of `Memory/`. Per area that has a `Direction.md`:

```bash
mkdir -p Direction
git mv Memory/<area>/Direction.md Direction/<area>.md
git rm -f Memory/Lexicon/processing-strategy.md   # superseded by Direction/Lexicon.md
```

The `git rm` line applies once, regardless of how many areas you have: it clears
the old Lexicon direction file, which is exactly the deletion described above
that `git checkout` cannot propagate for you. Left in place it keeps asserting
the pre-this-tier boundary ("Human gate on **Direction**... **Triage** — rare
Direction edits") against `Direction/Lexicon.md`'s current one, from a path
(`Memory/Lexicon/`) agents search but `lint_vault.py` never scanned — until now:
it warns if it finds this file.

Then sort each area file's body into `## Purpose`, `## Principles` and
`## Standards` — `lint_vault.py` rejects any other `##` section. Anything with a
date that can be missed is not a principle: it is an objective, and belongs in
`Objectives.md`.

```bash
python3 scripts/lexicon_init.py   # scaffolds Objectives.md and missing Direction files
python3 scripts/lint_vault.py     # must exit 0 when migration is complete
```

Migration is complete when `lint_vault.py` **exits 0** — not when it stops
warning about `Memory/<area>/Direction.md`: that warning disappears the moment
you `git mv` the file, before its body is sorted. The real completion test is
the section whitelist: every `##` heading on `Direction/<area>.md` other than
Purpose, Principles or Standards is an **error**, not a warning, so expect a
wall of errors right after the `git mv` — that's expected, and it clears once
the body is sorted. See [OBJECTIVES.md](OBJECTIVES.md) for what belongs in each
section.

## Customizing without forking the engine

Don't edit the shipped rules/skills in place — your edits would be overwritten on the next sync. Instead:

- **Vault-specific guidance** (your topic slugs, routing conventions, folder quirks): put it in `.cursor/rules/local-<name>.mdc`. Cursor loads it alongside the shipped rules; the sync never touches `local-*` files.
- **Registries** (`Metadata/*_registry.md`) are content — edit freely; they are never synced.

## Contributing improvements back

If you improve a shipped rule/skill/script in your vault:

1. **Generalize it** — remove your area names, people, paths, and domain-specific topic lists (those belong in your `local-*.mdc`).
2. Open a PR against the template repo.

This keeps one engine everyone shares, with personal knowledge and conventions layered locally.
