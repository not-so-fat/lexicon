# Tag Registry

All tags in Lexicon frontmatter must appear here.
Tags describe *properties of the interaction*, not subjects (use frontmatter `topics` for subjects).

**Maintained by:** user only. Cursor must never add new tags — only use what is listed here.
If Cursor encounters a meeting quality not covered, it should note it in the meeting note
and let the user decide whether to add a new tag.

## Pipeline tags (auto-assigned by scripts — never add manually)

| Tag | Applied to | Meaning |
|-----|-----------|---------|
| transcript | Transcript files | Raw transcript, not yet summarized |
| fireflies | Fireflies transcripts | Source: Fireflies |
| manual | Manual transcripts | Source: manual input |
| meeting | Transcript + Meeting note files | Related to a meeting |

## Property tags (assigned during summarize)

Apply when the meeting note has this *quality*. Max 3 per file.

| Tag | When to apply |
|-----|--------------|
| key-decision | A significant, durable decision was made |
| feedback | Explicit feedback was given or received |
| follow-up-needed | Open items requiring future action |
| sensitive | Content requires discretion (HR, compensation, legal) |

## Aliases (do NOT use — map to canonical)

| Alias | Use instead |
|-------|------------|
| decision | key-decision |
| decisions | key-decision |

## What NOT to tag (use topics or projects instead)

- Subject matter (hiring, pricing, onboarding) → frontmatter `topics`
- Life context (career, partnership) → `project` field or `topics`
