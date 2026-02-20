# Project Registry

Projects organize knowledge by context. Each project gets its own
subdirectories under Meetings/, People/, and Memory/.

**Maintained by:** user only. Cursor must never add new projects — only use what is
listed here. If a meeting doesn't fit any project, use `general` and flag it for the user.

| Project slug | Description | Default for account |
|-------------|-------------|-------------------|
| personal | Personal product work, side projects | personal |
| friendship | Non-work personal relationships | — |
| career | Career development, job search, mentoring | — |
| company | Day-job work (company context) | acme |
| general | Cross-cutting or unclassifiable | — |

## How projects are assigned

1. **Fireflies fetch:** writes `project: <default>` from `PROJECT_<account>` env var. This is just a default.
2. **Summarize step:** may override the project if the meeting content clearly belongs to a different project listed here.
3. **Manual transcripts:** project is set in frontmatter at creation time.

The meeting note's `project` field determines all downstream routing (People, Memory).
