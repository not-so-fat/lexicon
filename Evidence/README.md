# Evidence

**Tier 2 — append-only, dated, one-line pointers.** Written only by distill.

```
Evidence/<area>/
  Product.md  Org.md  Me.md  Validation.md
  Partners/<Company>.md
  People/<Name>.md
  Topics/<slug>.md            # optional; slug registered in Metadata/topic_registry.md first
```

Every file is the same shape:

```markdown
# Evidence (append-only)
- YYYY-MM-DD — <one line, ~30 words / 240 chars of claim text — source links and #tags don't count> — Source: [[Meeting or Idea]]
```

**Contract:**
- **Append-only and permanent** — never compacted, drained, rewritten, or deleted.
- **Pointers, not summaries** — detail stays in the linked source note.
- Decided decisions are bullets with a `Decision:` prefix. *Pending* decisions are
  working state → `Synthesis/`.
- Distill lints what it touched before finishing: `python3 scripts/lint_vault.py --files <paths>`.

**What does NOT belong here:** what the evidence *means* (→ `Synthesis/<area>.md`,
rewritten in triage), raw notes (→ `Sources/`), principles (→ `Direction/`).
See [docs/MEMORY_MODEL.md](../docs/MEMORY_MODEL.md).
