# Keeping your vault up to date

Your vault starts as a clone of this repo. After that, **your content is yours** — updates only touch the engine.

## Engine vs content

| Engine (synced from template) | Content (never synced — yours) |
|---|---|
| `.cursor/rules/`, `.cursor/skills/`, `.cursor/templates/` | `Meetings/`, `Memory/` (except `Memory/Lexicon/`), `People/`, `Ideas/`, `Transcripts/` |
| `scripts/`, `Memory/Lexicon/` (process charter) | `Metadata/` (registries, recap logs, `User.md`) |
| `docs/`, `README.md`, `requirements.txt`, `.env.example` | `.env`, `.cursor/rules/local-*.mdc` |

## Recommended setup (private vault + template upstream)

Keep your vault in your **own private repo** and pull engine updates from the template:

```bash
# once — inside your vault
git remote rename origin template        # if you cloned this repo directly
git remote add origin <your-private-repo-url>
git push -u origin main

# whenever you want updates
git fetch template
git checkout template/main -- .cursor/rules .cursor/skills .cursor/templates scripts docs Memory/Lexicon README.md requirements.txt .env.example
git diff --stat                          # review what changed
# commit to your private repo as usual
```

`git checkout template/main -- <paths>` overwrites only files the template ships. Files that exist only in your vault — `local-*.mdc` rules, extra scripts, all content — are untouched.

## Customizing without forking the engine

Don't edit the shipped rules/skills in place — your edits would be overwritten on the next sync. Instead:

- **Project-specific guidance** (your topic slugs, routing conventions, folder quirks): put it in `.cursor/rules/local-<name>.mdc`. Cursor loads it alongside the shipped rules; the sync never touches `local-*` files.
- **Registries** (`Metadata/*_registry.md`) are content — edit freely; they are never synced.

## Contributing improvements back

If you improve a shipped rule/skill/script in your vault:

1. **Generalize it** — remove your project names, people, paths, and domain-specific topic lists (those belong in your `local-*.mdc`).
2. Open a PR against the template repo.

This keeps one engine everyone shares, with personal knowledge and conventions layered locally.
