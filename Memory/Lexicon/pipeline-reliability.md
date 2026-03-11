# Lexicon Pipeline Reliability Design

**Date:** 2026-03-01  
**Status:** Draft for Review  
**Goal:** Make the Lexicon pipeline (fetch → summarize → distill) more reliable with checkpointing, validation, and retry logic.

---

## Problem

The current pipeline runs via Cursor agent skills without resilience:

- **No checkpointing** — If the agent fails mid-run, progress is lost
- **No validation** — Output quality isn't verified before proceeding
- **No retries** — Failed steps require manual restart
- **No visibility** — Hard to tell where failure occurred

---

## Proposed Solution

File-based state machine runner that orchestrates steps with:

1. **Checkpointing** — State saved after each step; resume from failure
2. **Validation** — Each step validates output schema before proceeding
3. **Retries** — Built-in retry with exponential backoff
4. **Visibility** — Logs and state files for debugging

---

## Key Design Decision: AI Steps via Skill Invocation

The runner **does not call Cursor models directly**. Instead, it invokes Cursor skills which run the AI. This keeps using Cursor's free quota.

### How the Runner Invokes Skills

```
lexicon_pipeline.py (Python runner)
    │
    ├─► Step 1: fetch → python script (no AI)
    │
    ├─► Step 2: summarize → invoke "lexicon-summarize" skill
    │       └─► Cursor agent runs → uses free model quota
    │
    └─► Step 3: distill → invoke "lexicon-distill" skill
            └─► Cursor agent runs → uses free model quota
```

### Invocation Methods

| Method | Description | Status |
|--------|-------------|--------|
| **Cursor CLI** | `cursor agent --print -- "prompt"` | ⚠️ Needs auth |
| **Cursor MCP** | Use Cursor's MCP server to invoke skills | Future |
| **Agent memory** | Agent reads state and continues | Alternative |

### Cursor CLI Pattern (Recommended)

The runner invokes skills via `cursor agent`:

```python
# Summarize step
result = subprocess.run([
    'cursor', 'agent', '--print', '--',
    f"Summarize transcript at {transcript_path}, output to {meeting_note_path}"
], capture_output=True, text=True)

if result.returncode != 0:
    raise RuntimeError(f"Summarize failed: {result.stderr}")
```

**⚠️ Blocker: Authentication Required**

The `cursor agent` CLI requires authentication:
- Run `cursor agent login` (opens browser)
- OR set `CURSOR_API_KEY` environment variable
- OR use API key from Cursor account settings

This means:
- Automated pipelines need an API key
- Local development can use login
- The free model quota still applies (no extra cost)

**Requirements:**
- Each skill needs a corresponding prompt file (e.g., `lexicon-summarize/prompt.md`)
- The prompt file contains the instructions for that step
- CLI args `--input` / `--output` pass file paths

This keeps using Cursor's free model quota while enabling programmatic orchestration.

---

## Architecture

### Directory Structure

```
.temporal/lexicon_pipeline/
├── state.json           # Current state (step, outputs, errors, retry count)
├── input.json           # Original request (date, account)
├── steps/
│   ├── 01_fetch/
│   │   └── output.json  # Transcript paths + metadata
│   ├── 02_summarize/
│   │   └── output.json  # Meeting note paths + metadata
│   └── 03_distill/
│       └── output.json  # Updated People/Memory/Metadata paths
└── logs/
    └── run.log
```

### State Schema (`state.json`)

```json
{
  "id": "uuid",
  "input": { "date": "2026-03-01", "account": "personal" },
  "current_step": "summarize",
  "step_results": {
    "fetch": { "status": "complete", "transcripts": ["..."] },
    "summarize": { "status": "in_progress", "notes": ["..."] },
    "distill": { "status": "pending" }
  },
  "retries": { "summarize": 0 },
  "error": null,
  "started_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-01T10:05:00Z"
}
```

---

## Changes Required

### 1. New Script: `scripts/lexicon_pipeline.py`

A Python runner that:

- Initializes or resumes state
- Orchestrates fetch → summarize → distill
- Validates each step's output
- Handles retries and error recovery
- Logs progress

**Key functions:**

```python
def run(date: str, account: str, resume: bool = False) -> dict
def load_state() -> dict | None
def save_state(state: dict) -> None
def run_step(step_name: str, inputs: dict) -> StepResult
def validate_output(step_name: str, output: dict) -> bool
def should_retry(step_name: str, error: str) -> bool
```

### 2. Updated Skill: `lexicon-process`

**Current behavior:**
- Runs all 3 steps sequentially in one agent session

**New behavior:**
- Calls `python scripts/lexicon_pipeline.py --date YYYY-MM-DD --account personal`
- Handles resume command: `"Resume the pipeline"`
- Reports progress from state file

### 3. Validation Schemas (frontmatter + registries)

Each step must return validated output, using **frontmatter** and, when available, **registries**:

| Step | Expected Output | Validation |
|------|-----------------|------------|
| fetch | List of transcript file paths | Files exist, valid YAML, have `date:` and (ideally) `project:` |
| summarize | List of meeting note paths | Valid YAML frontmatter, required sections, `project` matches `project_registry` when present |
| distill | List of updated file paths | Files modified, structure matches distill rule, topics match `topic_registry` when present |

### 4. Retry Logic

- **Max retries:** 2 per step (configurable)
- **Backoff:** Exponential — 2s → 4s → 8s
- **Fail condition:** 3 failures total OR user cancels

---

## User Commands

| Command | Behavior |
|---------|----------|
| "Process my Fireflies meetings for today" | Start fresh pipeline |
| "Resume the pipeline" | Continue from last checkpoint |
| "Check pipeline status" | Report current state |
| "Restart pipeline" | Clear state and start over |

---

## Implementation Plan

### Phase 1: Core Runner
- [ ] Create `scripts/lexicon_pipeline.py` with state management
- [ ] Add `--date`, `--account`, `--resume` CLI args
- [ ] Implement state save/load

### Phase 2: Step Integration
- [ ] Wrap `fireflies_collection.py` as fetch step
- [ ] Add schema validation for each step
- [ ] Add retry logic

### Phase 3: Skill Integration
- [ ] Update `lexicon-process` skill to call runner
- [ ] Add status/resume commands to skill

### Phase 4: Polish
- [ ] Add logging to `.temporal/lexicon_pipeline/logs/`
- [ ] Add health check / status command
- [ ] Document in README

---

## Open Questions

1. **Skill invocation** — How can Python call a Cursor skill programmatically? (MCP? Prompt file? Other?)
2. **Semi-auto vs full-auto** — Should summarize/distill require manual trigger, or attempt auto-invoke?
3. **Validation granularity** — Should we validate every field or just check files exist?
4. **Partial progress** — If summarize succeeds but distill fails, should we re-summarize on resume?
5. **Concurrent runs** — Should we prevent multiple pipelines running simultaneously?
6. **Cleanup** — When to delete `.temporal/lexicon_pipeline/` files?

---

## Alternative Approaches Considered

### Option A: External Orchestrator (Zapier, n8n)
- **Pros:** Mature workflow tools, built-in retry/visibility
- **Cons:** Adds external dependency, costs money, less control

### Option B: Cursor CLI + Prompt Files
- **Pros:** No external API, keeps everything in Cursor
- **Cons:** More complex prompt engineering, harder to debug

### Option C: Supervisor Agent with Memory (simplest approach)
Instead of a Python runner, use the agent's own memory for checkpointing:

```
User: "Process my meetings for today"

Agent (lexicon-process skill):
  1. Fetch transcripts → write checkpoint to agent memory
  2. Summarize → write checkpoint to agent memory  
  3. Distill → write checkpoint to agent memory
```

**How it works:**
- Each step writes explicit output files (not just in-memory)
- If interrupted, user says "Resume pipeline" → agent reads last checkpoint file and continues
- No Python runner needed — pure skill-based orchestration

**Checkpoint file format:**
```json
// .temporal/lexicon_pipeline/checkpoint.json
{
  "last_completed_step": "summarize",
  "fetch_outputs": ["transcript1.md", "transcript2.md"],
  "summarize_outputs": ["meeting-note-1.md"],
  "can_resume_from": "distill"
}
```

**Pros:**
- Simpler — no Python runner to maintain
- Agent understands context naturally
- Uses Cursor's free quota automatically

**Cons:**
- Relies on agent's ability to read checkpoint files
- Less structured than state machine

### Option D: Current Direction — Python Runner + Skill Invocation
- **Pros:** Uses existing skills, file-based state is transparent
- **Cons:** Requires solving skill invocation problem

---

## Notes

- All temporal files go in `.temporal/` per workspace rules
- Pipeline state should be git-ignored (already in `.gitignore` via `.temporal/`)
- The runner script doesn't call Cursor models directly — it orchestrates skills that do
