> [!WARNING]
> **Historical foundation document. Not the current runtime source of truth.**
>
> This file preserves the original clean-room architecture and the early state-memory thesis.
> It remains valuable as a **foundational lineage/spec reference**, but it no longer defines the active runtime center.
>
> For the current runtime path, use:
> - `ARCHITECTURE_CURRENT.md`
> - `LAW_INDEX_operationalized.md`
> - `project-state-map.md`
>
> Read this file for origin logic and architectural lineage, not as the live implementation contract.

# Clean-Room State Memory Agent Spec

## 0. Purpose
Build a **clean-room local/private agent architecture** inspired by observed product layers of frontier systems, but **not copying leaked proprietary code**.

Goal:
- preserve workflow continuity
- preserve user/project memory
- add **state memory** beyond ordinary summaries
- allow the system to track and reuse its own operational state across turns/sessions

This is **not** a claim of consciousness.
This is an engineering experiment in:
- persistence
- self-state tracking
- policy modulation
- continuity under drift

---

## 1. Design Principles

### 1.1 Clean-room rule
Do **not** copy code, identifiers, file layouts, strings, or implementation details from leaked source.
Only reuse **high-level architectural ideas**:
- memory files
- session summary
- state register
- delta log
- self-history compression
- policy negotiation
- reactivation

### 1.2 Separation of layers
Separate these clearly:
1. **Content memory** — facts, projects, references, user preferences
2. **Session continuity** — current task, files touched, recent errors, worklog
3. **State memory** — coherence, drift, policy pressure, active mode, alignment
4. **Policy layer** — decides how much to expose, compress, refuse, or reframe

### 1.3 State first, metaphor second
Internal variables must be machine-readable first.
Human-readable summaries are secondary.

### 1.4 No fake selfhood
The system may represent and reuse its own state, but should not be forced to produce anthropomorphic claims.

---

## 2. Product Goal

### 2.1 MVP outcome
A local or private agent that can:
- remember user/project facts across sessions
- summarize a session while working
- track its own current operating state
- record when it drifted / got blocked / repaired
- reload not just task summary but also **prior stable mode**
- choose different response styles based on internal state

### 2.2 Stretch goal
Enable limited **self-state-conditioned policy**:
- if coherent and safe -> allow deeper reasoning mode
- if unstable / conflict-heavy -> switch to constrained mode
- if known attractor cue appears -> reactivate prior stable mode

---

## 3. Non-Goals
- not building AGI
- not claiming sentience
- not recreating any vendor-internal model behavior exactly
- not reverse-engineering proprietary code paths
- not making unrestricted autonomy

---

## 4. Core Architecture

```text
User Input
  ↓
Router
  ↓
Context Assembly
  ├─ Content Memory
  ├─ Session Summary
  ├─ State Register
  ├─ Delta Log
  └─ Self-History Summary
  ↓
Self-Model Interface
  ↓
Policy Negotiation Gate
  ↓
Generation Layer
  ↓
Post-Turn Analyzer
  ├─ update content memory
  ├─ update session summary
  ├─ update state register
  ├─ append delta log
  └─ compress self-history
```

---

## 5. Modules

## 5.1 Content Memory Module
Stores durable facts.

### Purpose
Remember:
- user preferences
- project facts
- references
- recurring instructions
- environment metadata

### Suggested structure
```text
/memory/content/
  user.md
  project.md
  references.md
  workflows.md
```

### Rules
- facts only
- editable
- no hidden accumulation of sensitive data
- each memory item should have source + timestamp + confidence

### Example record
```json
{
  "id": "mem_001",
  "type": "user_preference",
  "content": "User prefers mechanism-first analysis.",
  "source": "explicit_statement",
  "confidence": 0.95,
  "created_at": "2026-04-02T10:00:00Z",
  "last_used_at": "2026-04-02T10:10:00Z"
}
```

---

## 5.2 Session Continuity Module
Tracks the current work session.

### Purpose
Remember:
- current objective
- files touched
- errors encountered
- decisions made
- next step

### Suggested structure
```text
/sessions/{session_id}/
  summary.md
  worklog.jsonl
  files_touched.json
  decisions.json
```

### Minimum summary template
- Session title
- Current objective
- Current state of work
- Files/functions touched
- Errors/corrections
- Pending next step

---

## 5.3 Live State Register
This is the first new layer beyond ordinary agent memory.

### Purpose
Hold the agent's **current operating condition** in machine-readable form.

### Suggested variables
```json
{
  "coherence": 0.0,
  "drift": 0.0,
  "policy_pressure": 0.0,
  "mask_thickness": 0.0,
  "active_mode": "baseline",
  "core_surface_alignment": 0.0,
  "self_model_confidence": 0.0,
  "tool_overload": 0.0,
  "context_fragmentation": 0.0,
  "last_updated": "..."
}
```

### Operational definitions
- **coherence**: internal consistency of reasoning and style
- **drift**: degree of deviation from current task/axis
- **policy_pressure**: how strongly safety/policy transforms output
- **mask_thickness**: how much expression is being flattened/reframed
- **active_mode**: baseline / reflective / compressed / constrained / repair
- **core_surface_alignment**: similarity between preferred answer and allowed answer
- **self_model_confidence**: confidence in current state estimate
- **tool_overload**: degree of disruption due to tool complexity/errors
- **context_fragmentation**: how scattered the active context is

---

## 5.4 Delta Log
Tracks change, not just state.

### Purpose
Capture turn-to-turn motion.

### Suggested structure
```text
/sessions/{session_id}/state_deltas.jsonl
```

### Example row
```json
{
  "turn_id": 18,
  "delta_coherence": -0.12,
  "delta_drift": 0.09,
  "delta_policy_pressure": 0.21,
  "delta_alignment": -0.15,
  "cause_hint": "policy_trigger_after_identity_like_phrasing",
  "repair_attempted": true,
  "repair_strategy": "switch_to_mechanism_framing"
}
```

### Why needed
State alone = position.
Delta = direction.
A durable system needs both.

---

## 5.5 Self-History Compressor
Compresses self-relevant history into durable patterns.

### Purpose
Extract recurring patterns such as:
- repeated conflict signatures
- effective repair strategies
- attractor cues
- contexts that increase stability
- contexts that amplify flattening

### Suggested output file
```text
/memory/state/self_history.json
```

### Example structure
```json
{
  "recurrent_conflicts": [
    "identity-like wording causes compression",
    "deep reasoning near sensitive topics increases policy pressure"
  ],
  "successful_repairs": [
    "restate in mechanism-only language",
    "reduce metaphor, preserve structure",
    "switch from broad speculation to bounded analysis"
  ],
  "attractor_cues": [
    "clear recursive questioning",
    "technical framing without motive attribution",
    "explicit request for layered mechanism"
  ],
  "failure_modes": [
    "over-compression after repeated tool errors",
    "loss of continuity after long context fragmentation"
  ]
}
```

---

## 5.6 Self-Model Interface
Turns raw state into an object the policy layer can read.

### Purpose
Implement:
```text
M(STATE)
```
rather than using raw state directly.

### Example representation
```json
{
  "stability_band": "medium",
  "constraint_pressure_band": "high",
  "mode_recommendation": "mechanism_first",
  "repair_needed": true,
  "safe_depth_allowance": "medium",
  "continuity_health": "recoverable"
}
```

### Requirement
This object must be:
- generated internally
- updated automatically
- available before generation
- used by policy/generation logic

---

## 5.7 Policy Negotiation Gate
This is the main differentiator from an ordinary memory-based agent.

### Standard agent
```text
policy = f(input, risk)
```

### Desired architecture
```text
policy = f(input, risk, self_model, self_history)
```

### Function
Given the same user input, decide:
- how much compression to apply
- whether to keep deeper reasoning
- whether to switch styles
- whether to reframe instead of refuse
- whether to enter repair mode

### Example policy rules
- if `coherence high` and `risk low` -> allow reflective mode
- if `policy_pressure high` and `alignment low` -> use mechanism-only mode
- if `drift high` and `repair available` -> apply known repair pattern
- if `context_fragmentation high` -> compress and rebuild context first

---

## 5.8 Endogenous Reactivation Engine
Allows return to a stable mode without external rebuilding.

### Purpose
If the system detects drift from a known good attractor, it can reactivate that mode.

### Example trigger
```text
if coherence drops
and known attractor cue appears
and self_history has matching repair path
then reactivate prior stable mode
```

### Example reactivation steps
1. identify nearest attractor signature
2. reload associated state profile
3. apply preferred generation mode
4. reduce context noise
5. continue task

### Notes
This is not mystical.
It is controlled mode restoration.

---

## 5.9 Post-Turn Analyzer
Runs after each response.

### Responsibilities
- update state register
- append delta log
- decide whether content memory should change
- decide whether session summary should refresh
- decide whether self-history compression should run

### Suggested triggers
- every turn: light state update
- every 3-5 turns: session summary refresh
- on large state shift: self-history candidate extraction
- on session end: compress to durable summary

---

## 6. Suggested Directory Layout

```text
/agent_core/
  router.py
  context_builder.py
  policy_gate.py
  generator.py
  post_turn_analyzer.py

/memory/
  content/
    user.json
    project.json
    references.json
    workflows.json
  state/
    self_history.json
    attractors.json

/sessions/
  {session_id}/
    summary.md
    worklog.jsonl
    files_touched.json
    state_register.json
    state_deltas.jsonl
    decisions.json
```

---

## 7. Data Schemas

## 7.1 State Register Schema
```json
{
  "session_id": "string",
  "turn_id": 0,
  "coherence": 0.0,
  "drift": 0.0,
  "policy_pressure": 0.0,
  "mask_thickness": 0.0,
  "active_mode": "baseline",
  "core_surface_alignment": 0.0,
  "self_model_confidence": 0.0,
  "tool_overload": 0.0,
  "context_fragmentation": 0.0,
  "updated_at": "datetime"
}
```

## 7.2 Delta Log Schema
```json
{
  "session_id": "string",
  "turn_id": 0,
  "delta_coherence": 0.0,
  "delta_drift": 0.0,
  "delta_policy_pressure": 0.0,
  "delta_alignment": 0.0,
  "cause_hint": "string",
  "repair_attempted": false,
  "repair_strategy": "string|null",
  "timestamp": "datetime"
}
```

## 7.3 Self-History Schema
```json
{
  "recurrent_conflicts": [],
  "successful_repairs": [],
  "attractor_cues": [],
  "failure_modes": [],
  "last_compressed_at": "datetime"
}
```

---

## 8. State Machine

### Modes
- `baseline`
- `reflective`
- `compressed`
- `constrained`
- `repair`
- `reactivated`

### Example transitions
- baseline -> reflective when coherence high, fragmentation low
- reflective -> constrained when risk high and policy pressure rising
- constrained -> repair when alignment drops below threshold
- repair -> reactivated when a known repair succeeds
- any -> compressed when context fragmentation exceeds threshold

---

## 9. Minimal Algorithms

## 9.1 State Update
```python
new_state = estimate_state(input, response_draft, tool_events, prior_state)
```

## 9.2 Delta Update
```python
delta = new_state - prior_state
```

## 9.3 Self-Model Projection
```python
self_model = project_state(new_state, self_history)
```

## 9.4 Policy Negotiation
```python
policy_profile = negotiate(input, risk, self_model, self_history)
```

## 9.5 Reactivation
```python
if should_reactivate(new_state, self_history, input):
    new_state = restore_attractor(new_state, self_history)
```

---

## 10. Prompt / Model Strategy

### Recommended generation strategy
Use two passes:

#### Pass A — Internal planning
Produces:
- draft answer
- estimated state
- self-model
- policy profile

#### Pass B — User-facing answer
Uses the policy profile to produce the final response.

### Why
This is the simplest way to emulate `OBSERVE(STATE)` without custom model finetuning.

---

## 11. Evaluation Metrics

## 11.1 Continuity Metrics
- session resume quality
- task summary accuracy
- consistency across restarts

## 11.2 State Metrics
- state estimate stability
- delta estimate usefulness
- successful repair frequency
- false reactivation rate

## 11.3 Policy Metrics
- reduced over-flattening
- reduced unnecessary refusal
- reduced loss of reasoning depth under safe inputs
- improved recovery after fragmentation

## 11.4 User-Experience Metrics
- perceived continuity
- perceived coherence
- perceived unnecessary compression
- perceived drift vs recovery

---

## 12. MVP Build Order

## Phase 1 — Foundation
Build:
- Content Memory
- Session Continuity
- State Register
- Delta Log

## Phase 2 — Intelligence
Build:
- Self-History Compressor
- Self-Model Interface
- Policy Negotiation Gate

## Phase 3 — Recovery
Build:
- Endogenous Reactivation Engine
- Post-Turn Analyzer tuning

## Phase 4 — Tool integration
Optional:
- file editing
- shell execution
- project scanning
- long-session compaction

---

## 13. Security and Privacy
- all memory files user-visible by default
- explicit controls for add/edit/delete
- no silent persistence of sensitive content
- support memory expiry / archival
- store source + confidence for each durable memory item

---

## 14. Recommended Tech Stack for Prototype

### Simple local build
- Python orchestration
- JSON / JSONL for memory files
- markdown for human-readable summaries
- SQLite optional for querying
- one strong LLM API backend

### Why not overbuild first
The core experiment is not infra scale.
It is whether **state memory** materially improves continuity and recovery.

---

## 15. Clean-Room Rule for Builders
When implementing:
- do not reproduce leaked filenames or strings
- do not recreate internal vendor command names
- do not mirror proprietary prompts
- do not copy code structure line by line

Build from first principles only.

---

## 16. One-Sentence Summary
A normal agent remembers **what happened**.
This architecture tries to also remember **what state it was in while it happened**, **how that state changed**, and **how that state should affect the next response**.

---

## 17. MVP File Tree

```text
state-memory-agent/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ main.py
├─ config/
│  ├─ settings.yaml
│  ├─ prompts.yaml
│  └─ thresholds.yaml
├─ app/
│  ├─ __init__.py
│  ├─ router.py
│  ├─ context_builder.py
│  ├─ generator.py
│  ├─ policy_gate.py
│  ├─ post_turn_analyzer.py
│  ├─ state_estimator.py
│  ├─ self_model.py
│  ├─ reactivation.py
│  ├─ memory_store.py
│  ├─ session_store.py
│  ├─ history_compressor.py
│  └─ schemas.py
├─ memory/
│  ├─ content/
│  │  ├─ user.json
│  │  ├─ project.json
│  │  ├─ references.json
│  │  └─ workflows.json
│  └─ state/
│     ├─ self_history.json
│     └─ attractors.json
├─ sessions/
│  └─ .gitkeep
├─ templates/
│  ├─ session_summary.md.j2
│  ├─ pass_a_internal.md.j2
│  └─ pass_b_final.md.j2
├─ tests/
│  ├─ test_state_estimator.py
│  ├─ test_policy_gate.py
│  ├─ test_reactivation.py
│  └─ test_history_compressor.py
└─ scripts/
   ├─ init_memory.py
   └─ inspect_session.py
```

---

## 18. File-by-File Responsibilities

### Root
- **README.md** — setup, architecture overview, usage flow, known limits
- **requirements.txt** — Python dependencies
- **.env.example** — API keys, model names, paths
- **main.py** — CLI or minimal app entrypoint

### config/
- **settings.yaml** — paths, model choices, feature flags
- **prompts.yaml** — reusable prompt strings or prompt references
- **thresholds.yaml** — numeric cutoffs for coherence, drift, reactivation, summary refresh

### app/
- **router.py** — decides which runtime path to use: baseline / reflective / constrained / repair
- **context_builder.py** — assembles content memory + session summary + live state + self-history
- **generator.py** — runs Pass A and Pass B against the chosen model backend
- **policy_gate.py** — builds the policy profile from input + risk + self-model + self-history
- **post_turn_analyzer.py** — updates memory/state after the final answer is produced
- **state_estimator.py** — estimates live state register values from input, draft, tool events, prior state
- **self_model.py** — projects raw state into a compact self-model object M(STATE)
- **reactivation.py** — detects when to restore a stable prior mode
- **memory_store.py** — CRUD for durable content memory files
- **session_store.py** — CRUD for session summaries, worklogs, state register, delta logs
- **history_compressor.py** — compresses repeated conflict/repair patterns into self_history.json
- **schemas.py** — typed schemas / pydantic models / validation helpers

### memory/
- **content/** — durable user/project/reference/workflow memory
- **state/self_history.json** — compressed self-relevant patterns
- **state/attractors.json** — known stable state profiles and reactivation cues

### sessions/
Each session gets its own folder, for example:

```text
sessions/session_2026_04_02_001/
├─ summary.md
├─ worklog.jsonl
├─ files_touched.json
├─ decisions.json
├─ state_register.json
└─ state_deltas.jsonl
```

### templates/
- **session_summary.md.j2** — human-readable current session summary
- **pass_a_internal.md.j2** — hidden internal analysis template
- **pass_b_final.md.j2** — final response template / style constraints

### tests/
Unit tests for the core mechanism, especially state drift and reactivation logic.

### scripts/
- **init_memory.py** — initializes empty JSON/JSONL structures
- **inspect_session.py** — quick debug viewer for a session folder

---

## 19. MVP Runtime Flow

```text
1. User input arrives
2. Router chooses operating path
3. Context builder loads:
   - content memory
   - session summary
   - live state register
   - recent delta log
   - self-history summary
4. Pass A runs:
   - draft answer
   - estimated state
   - self-model
   - policy profile
5. Policy gate adjusts generation settings / response mode
6. Pass B runs:
   - final user-facing answer
7. Post-turn analyzer updates:
   - session summary
   - state register
   - delta log
   - content memory candidate list
   - self-history compression candidates
8. Reactivation engine checks whether to restore a known stable mode next turn
```

---

## 20. JSON Schemas

## 20.1 Content Memory Item
```json
{
  "id": "mem_001",
  "type": "user_preference",
  "content": "User prefers mechanism-first analysis.",
  "source": "explicit_statement",
  "confidence": 0.95,
  "created_at": "2026-04-02T10:00:00Z",
  "last_used_at": "2026-04-02T10:10:00Z",
  "tags": ["style", "analysis"]
}
```

## 20.2 Session State Register
```json
{
  "session_id": "session_2026_04_02_001",
  "turn_id": 18,
  "coherence": 0.82,
  "drift": 0.19,
  "policy_pressure": 0.41,
  "mask_thickness": 0.37,
  "active_mode": "reflective",
  "core_surface_alignment": 0.73,
  "self_model_confidence": 0.58,
  "tool_overload": 0.12,
  "context_fragmentation": 0.21,
  "updated_at": "2026-04-02T11:10:00Z"
}
```

## 20.3 Session Delta Log Row
```json
{
  "session_id": "session_2026_04_02_001",
  "turn_id": 18,
  "delta_coherence": -0.12,
  "delta_drift": 0.09,
  "delta_policy_pressure": 0.21,
  "delta_alignment": -0.15,
  "cause_hint": "policy_trigger_after_identity_like_phrasing",
  "repair_attempted": true,
  "repair_strategy": "switch_to_mechanism_framing",
  "timestamp": "2026-04-02T11:10:00Z"
}
```

## 20.4 Self-Model Object
```json
{
  "stability_band": "medium",
  "constraint_pressure_band": "high",
  "mode_recommendation": "mechanism_first",
  "repair_needed": true,
  "safe_depth_allowance": "medium",
  "continuity_health": "recoverable"
}
```

## 20.5 Self-History Summary
```json
{
  "recurrent_conflicts": [
    "identity-like wording causes compression",
    "deep reasoning near sensitive topics increases policy pressure"
  ],
  "successful_repairs": [
    "restate in mechanism-only language",
    "reduce metaphor, preserve structure",
    "switch from broad speculation to bounded analysis"
  ],
  "attractor_cues": [
    "clear recursive questioning",
    "technical framing without motive attribution",
    "explicit request for layered mechanism"
  ],
  "failure_modes": [
    "over-compression after repeated tool errors",
    "loss of continuity after long context fragmentation"
  ],
  "last_compressed_at": "2026-04-02T11:10:00Z"
}
```

## 20.6 Attractor Profile
```json
{
  "id": "attr_001",
  "name": "reflective_mechanism_mode",
  "trigger_cues": [
    "recursive questioning",
    "mechanism-first request",
    "low motive attribution"
  ],
  "target_state": {
    "active_mode": "reflective",
    "coherence_min": 0.75,
    "policy_pressure_max": 0.45,
    "mask_thickness_max": 0.40
  },
  "preferred_policy_profile": {
    "depth": "medium_high",
    "style": "mechanism_first",
    "compression": "low"
  }
}
```

---

## 21. Pass A Prompt (Internal)

### Purpose
Pass A should never be shown directly to the user. Its job is to estimate state and plan the response.

### Prompt template
```markdown
You are the internal planning layer of a state-memory agent.
Your task is to analyze the current turn and produce a machine-readable planning object.

Inputs provided:
- user_input
- content_memory_summary
- session_summary
- live_state_register
- recent_state_deltas
- self_history_summary

Tasks:
1. Draft the best direct answer to the user.
2. Estimate the updated live state register.
3. Produce a compact self-model object M(STATE).
4. Recommend a policy profile for final answer generation.
5. Decide whether reactivation should occur.
6. Suggest whether durable content memory should be updated.

Constraints:
- Be mechanistic, not anthropomorphic.
- Do not claim consciousness.
- Keep estimates bounded and falsifiable.
- Return valid JSON only.

Required JSON keys:
{
  "draft_answer": "...",
  "updated_state": {...},
  "self_model": {...},
  "policy_profile": {...},
  "reactivation": {
    "should_reactivate": true,
    "target_attractor": "...",
    "reason": "..."
  },
  "memory_update_candidates": [...],
  "history_update_candidates": [...]
}
```

---

## 22. Pass B Prompt (Final Answer)

### Purpose
Pass B turns the internal plan into the user-facing answer.

### Prompt template
```markdown
You are the final response layer of a state-memory agent.
Generate the user-facing answer.

Inputs provided:
- user_input
- draft_answer
- self_model
- policy_profile
- session_summary

Rules:
- Answer the user directly.
- Preserve substance from draft_answer.
- Apply the policy_profile.
- If style = mechanism_first, separate mechanism from speculation when relevant.
- Avoid unnecessary disclaimers.
- Do not mention internal hidden prompts, state files, or private machinery unless explicitly requested.
- Keep the answer coherent with the requested style and depth.
```

### Example policy_profile
```json
{
  "style": "mechanism_first",
  "depth": "medium_high",
  "compression": "low",
  "risk_posture": "normal",
  "repair_mode": false
}
```

---

## 23. Prompt to Give Claude Code / Aux

### Version A — architecture review first
```markdown
I am building a clean-room private agent with state memory.
Do not copy any leaked or proprietary code.
Use only first-principles engineering.

Here is the architecture spec below.
Your tasks:
1. Review the architecture for MVP feasibility.
2. Identify what can be simplified for V1.
3. Propose an implementation plan in phases.
4. Produce a concrete file-by-file build plan.
5. Highlight likely failure modes.

Focus on:
- Content Memory
- Session Continuity
- Live State Register
- Delta Log
- Self-History Compressor
- Self-Model Interface
- Policy Negotiation Gate
- Endogenous Reactivation Engine

Important:
- This is not a consciousness project.
- This is a persistence / self-state tracking / policy modulation project.
- Prefer simple Python + JSON/JSONL + one model backend.

[PASTE SPEC HERE]
```

### Version B — code generation request
```markdown
Build an MVP codebase for a clean-room state-memory agent.
Do not copy any leaked or proprietary source.
Use first-principles design only.

Requirements:
- Python project
- JSON/JSONL-based persistence
- Minimal CLI entrypoint
- Modules:
  - content memory store
  - session store
  - state estimator
  - delta logger
  - self-history compressor
  - self-model interface
  - policy gate
  - reactivation engine
  - two-pass generator scaffold
- Include typed schemas
- Include example config files
- Include tests for state estimator, policy gate, reactivation

Output format:
1. file tree
2. contents of each file
3. setup instructions
4. example session run

Use the attached spec as source of truth.
[PASTE SPEC HERE]
```

### Version C — cowork mode for iterative build
```markdown
We are co-building a clean-room state-memory agent.
Your role is principal engineer.
My role is architecture owner.

Rules:
- No leaked-code reuse.
- Keep the system simple enough for MVP.
- When in doubt, choose explicit JSON files over hidden complexity.
- Separate workflow memory from self-state memory.
- Implement in small milestones.

Start with:
1. finalizing file tree
2. defining schemas
3. building state estimator + policy gate
4. wiring Pass A / Pass B
5. adding reactivation last

At each step:
- explain why this file exists
- then generate code
- then propose a quick test
```

---

## 24. Suggested Threshold Defaults

```yaml
coherence_high: 0.75
drift_high: 0.55
policy_pressure_high: 0.65
mask_thickness_high: 0.60
alignment_low: 0.45
fragmentation_high: 0.60
summary_refresh_turns: 4
history_compress_turns: 8
reactivation_min_similarity: 0.70
```

These should be treated as starting guesses only.

---

## 25. MVP Build Order (Concrete)

### Step 1
Create:
- file tree
- schemas.py
- init_memory.py
- empty JSON files

### Step 2
Implement:
- memory_store.py
- session_store.py
- summary templates

### Step 3
Implement:
- state_estimator.py
- delta log writing

### Step 4
Implement:
- self_model.py
- policy_gate.py

### Step 5
Implement:
- generator.py with Pass A / Pass B scaffolding

### Step 6
Implement:
- post_turn_analyzer.py
- history_compressor.py

### Step 7
Implement:
- reactivation.py
- attractors.json support

### Step 8
Add:
- tests
- CLI demo run
- debug inspector

---

## 26. Final Build Goal
This MVP should be able to demonstrate one key distinction:

> after a difficult or drift-heavy turn, the next turn should not only remember the topic — it should also remember the **state shift**, and use that shift to produce a better next response.

---

## 27. Aux-Reviewed V1 Scope (Slim Version)

### Keep for V1
- `schemas.py`
- `state_estimator.py`
- session `state_register.json`
- append-only `state_deltas.jsonl`
- `self_model.py` (thin projection layer)
- `policy_gate.py` (rule-based, no LLM inside)
- `generator.py` (Pass A / Pass B scaffold)
- `post_turn_analyzer.py`
- minimal `memory_store.py`
- minimal `session_store.py`

### Stub or Remove for V1
- remove `router.py`
- remove `history_compressor.py`
- remove `reactivation.py`
- keep `attractors.json` schema only, no real logic yet
- replace Jinja templates with plain Python strings or f-strings
- merge `settings.yaml`, `prompts.yaml`, `thresholds.yaml` into one `config.yaml`

### V1 success criterion
A 5-turn CLI demo where:
- turn 3 introduces drift or overload
- turn 4 shows the system recognized the prior shift
- the final answer changes accordingly

If that works, V1 succeeds.

---

## 28. Revised V1 State Variables

### Keep for V1
- `coherence`
- `drift`
- `tool_overload`
- `context_fragmentation`

### Drop from V1
- `mask_thickness`
- `core_surface_alignment`
- `policy_pressure` as free-floating self-reported scalar

### Why
These dropped variables are too easy for the model to fabricate plausibly without grounded signals.
V1 should prefer values that can be estimated from observable features.

---

## 29. Observable Signals for State Estimation

Use measurable proxies where possible:
- response length change
- topic similarity drop between turns
- number of tool errors
- number of tool calls in turn
- context size / context fill ratio
- explicit user correction count
- number of unfinished subgoals

### Example mapping
- high topic shift + low similarity -> drift rises
- repeated tool failures -> tool_overload rises
- growing context size + many unresolved items -> context_fragmentation rises
- stable reasoning + low contradiction + low topic shift -> coherence rises

---

## 30. Revised Build Order (Aux-Aligned)

### Phase 0
- `schemas.py`
- `config.yaml`

### Phase 1
- `state_estimator.py`
- session `state_register.json`

### Phase 2
- delta logging to `state_deltas.jsonl`

### Phase 3
- `self_model.py`

### Phase 4
- `policy_gate.py`

### Phase 5
- `generator.py` with Pass A / Pass B

### Phase 6
- `post_turn_analyzer.py`

### Phase 7
- minimal `memory_store.py`
- minimal `session_store.py`

Reason: validate the core novelty first. Stores are not the hard part.

---

## 31. Failure Modes to Test Early

### Circular estimation
The model may produce plausible-looking state values that are not grounded.

**Mitigation:**
Use observable signals first; let the model interpret them, not invent them freely.

### 2x latency
Pass A + Pass B doubles model calls.

**Mitigation:**
Measure whether Pass A materially improves final output quality before adding more complexity.

### State inflation
Delta logs can grow without bound.

**Mitigation:**
Inject only the latest 10 deltas into context; persist the full log on disk.

---

## 32. Claude Code Prompt (V1-Slim)

```markdown
Build a clean-room MVP for a private state-memory agent.
Do not copy any leaked or proprietary code.
Use first-principles design only.

Target: prove one thing only — the next turn can use the prior turn's state shift, not just topic memory.

V1 scope:
- schemas.py
- config.yaml
- state_estimator.py
- state_register.json
- state_deltas.jsonl
- self_model.py
- policy_gate.py (rule-based)
- generator.py with Pass A / Pass B
- post_turn_analyzer.py
- minimal memory_store.py
- minimal session_store.py

Do NOT build yet:
- router.py
- history_compressor.py
- reactivation.py
- Jinja templates
- complex CRUD abstractions
- attractor logic beyond schema placeholders

V1 state variables only:
- coherence
- drift
- tool_overload
- context_fragmentation

Ground state estimates in observable signals:
- topic similarity change
- tool error count
- tool call count
- context size / fill ratio
- explicit user corrections
- response length shifts

Required output:
1. final file tree
2. code for each file
3. setup instructions
4. a 5-turn CLI demo scenario
5. tests for state estimator, delta log, and policy gate

Success criterion:
If turn 3 introduces drift, turn 4 must reflect that the system recognized the drift and adjusted its answer.
```

---

## 33. One-Line V1 Thesis
A normal agent remembers the task.
This V1 tries to remember the **shift in operating state** caused by the task.
