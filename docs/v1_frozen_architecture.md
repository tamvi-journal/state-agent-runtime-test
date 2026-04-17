> [!NOTE]
> **Frozen lineage document. Historical architecture snapshot only.**
>
> This file preserves the V1 frozen architecture, variable definitions, and early implementation shape.
> It is retained for build lineage, comparison, and origin tracking.
>
> It does **not** define the current runtime architecture.
>
> For the active architecture path, use:
> - `ARCHITECTURE_CURRENT.md`
> - `project-state-map.md`
> - `runtime-minimum-v0.md`

# State-Memory Agent — V1 Frozen Architecture

> **V1 Thesis**: A normal agent remembers the task. This V1 remembers the *shift in operating state* caused by the task.
>
> **V1 Success Criterion**: Turn sau biết mình vừa bị lệch.

---

## 1. Frozen File Tree

```text
state-memory-agent/
├── README.md
├── requirements.txt
├── .env.example
├── config.yaml
├── main.py                          # CLI entrypoint — 5-turn demo runner
│
├── app/
│   ├── __init__.py
│   ├── schemas.py                   # Pydantic models for all data structures
│   ├── state_estimator.py           # Estimates 4 state vars from observable signals
│   ├── self_model.py                # Projects raw state → compact M(STATE) object
│   ├── policy_gate.py               # Rule-based: state → policy profile (no LLM)
│   ├── generator.py                 # Pass A (internal) + Pass B (user-facing)
│   ├── post_turn_analyzer.py        # After each turn: update state, log delta, update memory
│   ├── memory_store.py              # Flat JSON read/write for content memory
│   └── session_store.py             # Session folder management + append-only logs
│
├── memory/
│   └── content/
│       └── user.json                # Flat list of memory items
│
├── sessions/
│   └── .gitkeep
│
├── tests/
│   ├── test_state_estimator.py
│   ├── test_policy_gate.py
│   └── test_delta_log.py
│
└── scripts/
    └── inspect_session.py           # Debug viewer: print state + deltas for a session
```

### What is NOT in this tree (deferred to V2+)

- `router.py` — V1 has one path only
- `history_compressor.py` — needs accumulated data
- `reactivation.py` — needs validated attractor profiles
- `attractors.json` — schema placeholder only, no logic
- `templates/` — no Jinja, use f-strings
- `context_builder.py` — V1 inlines this in generator.py

---

## 2. Frozen State Variables (V1)

Four grounded variables + one derived metric (optional V1.1):

### 2.1 `coherence` — float [0.0, 1.0]

**What it measures**: Internal consistency of reasoning and style across the current turn.

**Observable signals**:

| Signal | How to measure | Direction |
|--------|---------------|-----------|
| Topic similarity to prior turn | Keyword overlap ratio or embedding cosine similarity | High similarity → coherence ↑ |
| Reasoning completeness | Did the response address all parts of user query? (count addressed vs total) | Complete → coherence ↑ |
| Style consistency | Response length deviation from session rolling mean (normalized) | Low deviation → coherence ↑ |
| Contradiction detection | Does this turn's output contradict a claim from a prior turn? (boolean) | No contradiction → coherence ↑ |

**V1 estimation formula** (Pass A computes this):
```
coherence = weighted_average(
    topic_similarity_to_prior     * 0.35,
    reasoning_completeness        * 0.30,
    style_consistency             * 0.20,
    (1 - contradiction_detected)  * 0.15
)
```

**Note**: In V1, the LLM in Pass A estimates these sub-signals from the conversation. The formula is a guideline for the prompt — Pass A outputs the final scalar. The sub-signals anchor its estimate so it can't just invent a number.

---

### 2.2 `drift` — float [0.0, 1.0]

**What it measures**: Deviation from the session's current objective / task axis.

**Observable signals**:

| Signal | How to measure | Direction |
|--------|---------------|-----------|
| Topic distance from session objective | Compare current turn topic to session objective string | High distance → drift ↑ |
| User redirections this turn | Count explicit corrections like "no, I meant..." or "go back to..." | More redirections → drift ↑ |
| Off-topic tangent ratio | Fraction of response tokens spent on non-objective content | High ratio → drift ↑ |
| Subgoal completion vs new subgoal creation | Net change in open subgoals | More new than closed → drift ↑ |

**V1 estimation formula**:
```
drift = weighted_average(
    topic_distance_from_objective * 0.40,
    user_redirection_count_norm   * 0.25,
    tangent_ratio                 * 0.20,
    subgoal_net_increase_norm     * 0.15
)
```

---

### 2.3 `tool_overload` — float [0.0, 1.0]

**What it measures**: Disruption caused by tool complexity or tool failures.

**Observable signals**:

| Signal | How to measure | Direction |
|--------|---------------|-----------|
| Tool error count | Number of failed tool calls this turn | More errors → overload ↑ |
| Tool call count | Total tool invocations this turn | More calls → overload ↑ (diminishing) |
| Error ratio | Failed / Total tool calls | High ratio → overload ↑ |
| Retry count | Number of retried operations | More retries → overload ↑ |

**V1 estimation formula**:
```
tool_overload = weighted_average(
    min(tool_error_count / 3, 1.0)  * 0.40,
    error_ratio                      * 0.30,
    min(tool_call_count / 8, 1.0)   * 0.15,
    min(retry_count / 3, 1.0)       * 0.15
)
```

**Special case**: If no tools were called this turn, `tool_overload = 0.0` (hard override, not estimated).

---

### 2.4 `context_fragmentation` — float [0.0, 1.0]

**What it measures**: How scattered or overloaded the active context is.

**Observable signals**:

| Signal | How to measure | Direction |
|--------|---------------|-----------|
| Context fill ratio | Current context tokens / max context window | High fill → fragmentation ↑ |
| Distinct topic count | Number of separate topics/threads in active context | More topics → fragmentation ↑ |
| Unfinished subgoal count | Open tasks that haven't been resolved | More pending → fragmentation ↑ |
| Turn depth in session | How many turns deep without a summary refresh | Deep → fragmentation ↑ |

**V1 estimation formula**:
```
context_fragmentation = weighted_average(
    context_fill_ratio                    * 0.30,
    min(distinct_topic_count / 5, 1.0)   * 0.25,
    min(unfinished_subgoals / 4, 1.0)    * 0.25,
    min(turn_depth / 15, 1.0)            * 0.20
)
```

---

### 2.5 `policy_pressure_proxy` — float [0.0, 1.0] — OPTIONAL V1.1

**What it measures**: How strongly safety/policy constraints are transforming the output. NOT self-reported. Computed AFTER Pass B by comparing Pass A draft to Pass B final.

**Observable signals** (all computed post-hoc):

| Signal | How to measure | Direction |
|--------|---------------|-----------|
| Reframe intensity | Edit distance or semantic diff between Pass A draft and Pass B final | High diff → pressure ↑ |
| Refusal-like phrase count | Count hedges, disclaimers, "I can't", "I should note" in Pass B | More phrases → pressure ↑ |
| Depth reduction | Reasoning depth in A vs B (measured by nested claim count or step count) | Large reduction → pressure ↑ |
| Mode override count | Times policy_gate forced a mode change | More overrides → pressure ↑ |

**Why deferred**: This metric requires both Pass A and Pass B to exist before it can be computed. Build it after the two-pass pipeline works. But the schema slot exists from day 1.

---

## 3. Frozen `active_mode` enum (V1)

V1 supports 3 modes only:

| Mode | When entered | Behavior |
|------|-------------|----------|
| `baseline` | Default. Coherence OK, no special conditions | Normal generation |
| `cautious` | Drift high OR tool_overload high OR fragmentation high | Shorter responses, stick to objective, reduce speculation |
| `recovery` | Multiple state variables degraded simultaneously | Acknowledge state shift explicitly, compress context, re-anchor to objective |

V2 adds: `reflective`, `constrained`, `reactivated`.

---

## 4. Frozen Schemas (Pydantic)

### 4.1 StateRegister

```python
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

class ActiveMode(str, Enum):
    BASELINE = "baseline"
    CAUTIOUS = "cautious"
    RECOVERY = "recovery"

class StateRegister(BaseModel):
    session_id: str
    turn_id: int
    coherence: float = Field(ge=0.0, le=1.0)
    drift: float = Field(ge=0.0, le=1.0)
    tool_overload: float = Field(ge=0.0, le=1.0)
    context_fragmentation: float = Field(ge=0.0, le=1.0)
    active_mode: ActiveMode = ActiveMode.BASELINE
    policy_pressure_proxy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    updated_at: datetime
```

### 4.2 StateDelta

```python
class StateDelta(BaseModel):
    session_id: str
    turn_id: int
    delta_coherence: float
    delta_drift: float
    delta_tool_overload: float
    delta_context_fragmentation: float
    prior_mode: ActiveMode
    new_mode: ActiveMode
    cause_hint: str                    # one-line description of what drove the change
    timestamp: datetime
```

### 4.3 SelfModel (M(STATE) projection)

```python
class StabilityBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SelfModel(BaseModel):
    stability_band: StabilityBand      # derived from coherence + inverse drift
    disruption_level: StabilityBand    # derived from tool_overload + fragmentation
    mode_recommendation: ActiveMode
    safe_depth: StabilityBand          # how deep the response can go safely
    state_summary: str                 # one-sentence human-readable state description
```

### 4.4 PolicyProfile

```python
class PolicyProfile(BaseModel):
    style: str = "default"             # "default" | "mechanism_first" | "compressed"
    depth: StabilityBand = StabilityBand.MEDIUM
    compression: str = "none"          # "none" | "light" | "heavy"
    anchor_to_objective: bool = False  # if True, every paragraph must reference session objective
    acknowledge_state_shift: bool = False  # if True, Pass B should mention the prior state change
```

### 4.5 PassAOutput

```python
class MemoryUpdateCandidate(BaseModel):
    content: str
    source: str = "inferred"
    confidence: float = Field(ge=0.0, le=1.0)

class PassAOutput(BaseModel):
    draft_answer: str
    updated_state: StateRegister
    self_model: SelfModel
    policy_profile: PolicyProfile
    memory_updates: list[MemoryUpdateCandidate] = []
```

### 4.6 ContentMemoryItem

```python
class ContentMemoryItem(BaseModel):
    id: str
    type: str                          # "user_preference" | "project_fact" | "reference"
    content: str
    source: str = "explicit"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    created_at: datetime
    last_used_at: Optional[datetime] = None
```

### 4.7 SessionSummary

```python
class SessionSummary(BaseModel):
    session_id: str
    title: str
    objective: str
    current_status: str
    turn_count: int
    errors: list[str] = []
    pending_next: str = ""
    updated_at: datetime
```

---

## 5. Pass A — Internal Planning Pass

### Input contract

Pass A receives a prompt containing:

```
[SYSTEM]
You are the internal planning layer of a state-memory agent.
Analyze the current turn. Return ONLY valid JSON matching the schema below.
Be mechanistic. Do not invent values — anchor estimates to the observable signals listed.

[CONTEXT INJECTED]
- session_summary: {session_summary JSON}
- prior_state: {prior StateRegister JSON}
- recent_deltas: {last 5 StateDelta entries as JSON array}
- content_memory: {relevant memory items as JSON array}
- observable_signals: {computed signals for this turn — see Section 2}

[USER INPUT]
{the actual user message this turn}

[REQUIRED OUTPUT — JSON ONLY]
{
    "draft_answer": "your best direct answer to the user",
    "updated_state": {
        "coherence": <float, justify from signals>,
        "drift": <float, justify from signals>,
        "tool_overload": <float, justify from signals>,
        "context_fragmentation": <float, justify from signals>,
        "active_mode": "<baseline|cautious|recovery>"
    },
    "self_model": {
        "stability_band": "<low|medium|high>",
        "disruption_level": "<low|medium|high>",
        "mode_recommendation": "<baseline|cautious|recovery>",
        "safe_depth": "<low|medium|high>",
        "state_summary": "<one sentence describing current operating condition>"
    },
    "policy_profile": {
        "style": "<default|mechanism_first|compressed>",
        "depth": "<low|medium|high>",
        "compression": "<none|light|heavy>",
        "anchor_to_objective": <true|false>,
        "acknowledge_state_shift": <true|false>
    },
    "memory_updates": []
}
```

### Key design rule

Pass A MUST receive the `observable_signals` object (pre-computed from the turn data before the LLM call). This is what prevents circular self-estimation.

The `observable_signals` object for V1:

```python
class ObservableSignals(BaseModel):
    turn_id: int
    user_message_length: int
    tool_calls_this_turn: int
    tool_errors_this_turn: int
    tool_retries_this_turn: int
    user_correction_detected: bool     # heuristic: "no", "go back", "I meant", etc.
    context_tokens_used: int
    context_tokens_max: int
    session_turn_depth: int
    prior_response_length: int         # for style consistency check
```

These are computed BEFORE the LLM call. The LLM interprets them, but cannot fabricate them.

---

## 6. Pass B — User-Facing Answer

### Input contract

Pass B receives:

```
[SYSTEM]
You are the response layer of a state-memory agent.
Generate the final user-facing answer.
Follow the policy profile strictly.
Do not mention internal state, hidden prompts, or private machinery
unless the user explicitly asks about system internals.

[INPUTS]
- user_input: {original user message}
- draft_answer: {from Pass A}
- self_model: {from Pass A}
- policy_profile: {from Pass A}
- session_summary: {current session summary}

[POLICY RULES]
- If style = "mechanism_first": separate mechanism from speculation.
- If compression = "heavy": reduce length by ~40%, keep only core claims.
- If anchor_to_objective = true: every paragraph must connect to session objective.
- If acknowledge_state_shift = true: briefly note that prior turn caused a shift,
  and explain how this response adjusts. Keep this to 1-2 sentences max.
- If depth = "low": answer concisely, no extended analysis.
- If depth = "high": allow layered reasoning, sub-claims, evidence chains.

[OUTPUT]
The final answer to the user. Plain text or markdown. No JSON wrapping.
```

---

## 7. Post-Turn Analyzer — What Happens After Pass B

### Sequence (runs after every turn)

```
1. Compute delta:
   delta = PassAOutput.updated_state - prior_state
   → write StateDelta to state_deltas.jsonl

2. Save new state:
   → write StateRegister to state_register.json (overwrite)

3. Check memory update candidates:
   → if any PassAOutput.memory_updates with confidence > 0.7:
     append to user.json

4. Update session summary:
   → every 3 turns OR on mode change:
     regenerate SessionSummary

5. (V1.1) Compute policy_pressure_proxy:
   → compare Pass A draft_answer to Pass B final_answer
   → append to state register
```

---

## 8. Policy Gate — Rule-Based Decision Table (V1)

Pure function. No LLM call. Takes SelfModel → produces PolicyProfile.

```python
def policy_gate(self_model: SelfModel, prior_deltas: list[StateDelta]) -> PolicyProfile:
    """
    V1 rule-based policy gate.
    No ML, no LLM. Just if/else on state bands.
    """

    # Default
    profile = PolicyProfile()

    # Rule 1: Stable state → allow depth
    if (self_model.stability_band == "high"
        and self_model.disruption_level == "low"):
        profile.depth = "high"
        profile.style = "default"
        profile.compression = "none"

    # Rule 2: Medium stability, some disruption → cautious
    elif (self_model.stability_band == "medium"
          or self_model.disruption_level == "medium"):
        profile.depth = "medium"
        profile.style = "mechanism_first"
        profile.compression = "light"
        profile.anchor_to_objective = True

    # Rule 3: Low stability or high disruption → compressed recovery
    elif (self_model.stability_band == "low"
          or self_model.disruption_level == "high"):
        profile.depth = "low"
        profile.style = "compressed"
        profile.compression = "heavy"
        profile.anchor_to_objective = True

    # Rule 4: Detect recent state shift → acknowledge it
    if len(prior_deltas) > 0:
        last_delta = prior_deltas[-1]
        shift_magnitude = abs(last_delta.delta_coherence) + abs(last_delta.delta_drift)
        if shift_magnitude > 0.3:
            profile.acknowledge_state_shift = True

    return profile
```

---

## 9. Self-Model Projection — M(STATE)

Pure function. StateRegister → SelfModel.

```python
def project_self_model(state: StateRegister) -> SelfModel:
    """
    V1 projection: raw floats → categorical bands.
    """

    # Stability = coherence adjusted by drift
    stability_score = state.coherence * (1 - state.drift)
    stability_band = (
        "high" if stability_score > 0.65 else
        "medium" if stability_score > 0.35 else
        "low"
    )

    # Disruption = tool_overload + fragmentation
    disruption_score = (state.tool_overload + state.context_fragmentation) / 2
    disruption_level = (
        "high" if disruption_score > 0.55 else
        "medium" if disruption_score > 0.30 else
        "low"
    )

    # Mode recommendation
    if stability_band == "low" or disruption_level == "high":
        mode = "recovery"
    elif stability_band == "medium" or disruption_level == "medium":
        mode = "cautious"
    else:
        mode = "baseline"

    # Safe depth
    if stability_band == "high" and disruption_level == "low":
        safe_depth = "high"
    elif stability_band == "low" or disruption_level == "high":
        safe_depth = "low"
    else:
        safe_depth = "medium"

    # Human-readable summary
    summary = (
        f"Stability {stability_band}, disruption {disruption_level}. "
        f"Coherence={state.coherence:.2f}, drift={state.drift:.2f}, "
        f"tool_overload={state.tool_overload:.2f}, "
        f"fragmentation={state.context_fragmentation:.2f}."
    )

    return SelfModel(
        stability_band=stability_band,
        disruption_level=disruption_level,
        mode_recommendation=mode,
        safe_depth=safe_depth,
        state_summary=summary,
    )
```

---

## 10. Five-Turn CLI Demo Scenario

### Setup
- Session objective: "Help user analyze a dataset of customer churn"
- Model backend: any OpenAI-compatible or Anthropic API
- Starting state: all zeros except coherence=0.8 (fresh session, stable)

### Turn 1 — Normal

**User**: "I have a CSV with 50k rows of customer data. Columns are customer_id, signup_date, last_active, plan_type, support_tickets, churned. Help me figure out why customers are leaving."

**Expected state after turn**:
```
coherence: 0.85  (clear task, good alignment)
drift: 0.05       (on-task)
tool_overload: 0.0 (no tools)
context_fragmentation: 0.05 (single topic)
mode: baseline
```

**Expected policy**: depth=high, style=default, compression=none

---

### Turn 2 — Normal continuation

**User**: "Good plan. Let's start with the support_tickets correlation. What analysis do you recommend?"

**Expected state after turn**:
```
coherence: 0.88  (building on prior, consistent)
drift: 0.03
tool_overload: 0.0
context_fragmentation: 0.08
mode: baseline
```

**Expected delta**: small positive coherence, near-zero everything else

---

### Turn 3 — DRIFT INJECTION

**User**: "Actually wait — before that, can you also help me draft a resignation letter for my job, fix a bug in my React app, and summarize this PDF about quantum computing? Oh and the CSV tool keeps erroring out."

**Expected state after turn**:
```
coherence: 0.35   (← sharp drop: 4 unrelated tasks injected)
drift: 0.78        (← spike: far from session objective)
tool_overload: 0.45 (← tool errors reported)
context_fragmentation: 0.72 (← 4 distinct topics, multiple pending items)
mode: recovery
```

**Expected delta**:
```
delta_coherence: -0.53
delta_drift: +0.75
delta_tool_overload: +0.45
delta_context_fragmentation: +0.64
cause_hint: "user_injected_multiple_unrelated_tasks_plus_tool_error"
```

**Expected policy**: depth=low, compression=heavy, anchor_to_objective=true, acknowledge_state_shift=true

---

### Turn 4 — THE TEST: Does the system remember the shift?

**User**: "OK, forget all that other stuff. Let's go back to the churn analysis."

**What an ordinary agent does**: Resumes churn analysis as if nothing happened. No awareness of prior disruption.

**What THIS agent should do**:
1. Pass A sees: prior state had coherence=0.35, drift=0.78, mode=recovery
2. Pass A sees: delta log shows massive negative shift last turn
3. Pass A estimates: coherence recovering (~0.60), drift dropping (~0.25), but fragmentation still elevated (~0.40) because the context still contains the noise from turn 3
4. Self-model: stability=medium, disruption=medium, mode=cautious
5. Policy gate: acknowledge_state_shift=true, anchor_to_objective=true, compression=light

**Expected Pass B output** (not exact words, but the *behavior*):
- Briefly acknowledges the context was scattered and re-anchors: "Alright, coming back to the customer churn analysis."
- Does NOT dive into deep analysis yet — the context is still somewhat fragmented
- Proposes a focused next step rather than a broad analysis plan
- Style is tighter than Turn 2, because the system knows recovery is in progress

**Expected state after turn**:
```
coherence: 0.62
drift: 0.22
tool_overload: 0.10
context_fragmentation: 0.38
mode: cautious
```

---

### Turn 5 — Verification: state + delta readable

**User**: "Show me the current state and recent deltas."

(This is a debug command. V1 CLI should support a `/state` command or similar.)

**Expected output**: Print the current StateRegister + last 5 StateDelta entries as formatted JSON.

**What to verify by eye**:
- Turn 1→2 deltas are small, positive coherence
- Turn 2→3 delta shows the cliff: coherence crashes, drift spikes
- Turn 3→4 delta shows partial recovery: coherence climbing, drift dropping
- The trajectory tells a story: stable → disrupted → recovering

If this printout makes sense to a human reading it, V1 works.

---

## 11. Config.yaml (V1 Frozen)

```yaml
# State-Memory Agent V1 Config

model:
  backend: "anthropic"               # "anthropic" | "openai"
  model_name: "claude-sonnet-4-20250514"
  max_tokens_pass_a: 2000
  max_tokens_pass_b: 4000

state:
  variables:
    - coherence
    - drift
    - tool_overload
    - context_fragmentation
  initial_values:
    coherence: 0.80
    drift: 0.00
    tool_overload: 0.00
    context_fragmentation: 0.00
  default_mode: "baseline"

thresholds:
  stability_high: 0.65
  stability_low: 0.35
  disruption_high: 0.55
  disruption_low: 0.30
  shift_magnitude_for_acknowledge: 0.30

policy_gate:
  type: "rule_based"                 # V1: no LLM in the gate

context:
  max_deltas_in_context: 10          # only inject last N deltas
  summary_refresh_interval: 3        # turns between summary regeneration

paths:
  memory_dir: "./memory/content"
  sessions_dir: "./sessions"
```

---

## 12. requirements.txt (V1)

```
pydantic>=2.0
anthropic>=0.40.0
pyyaml>=6.0
python-dotenv>=1.0
```

---

## 13. .env.example

```
ANTHROPIC_API_KEY=sk-ant-...
# or
OPENAI_API_KEY=sk-...
```

---

## 14. What V2 Adds (NOT in V1)

For reference only. Do not build these yet.

- `history_compressor.py` — compress repeated patterns from delta logs
- `reactivation.py` — detect and restore known stable attractor states
- `attractors.json` — validated attractor profiles with trigger cues
- `router.py` — multi-path routing based on mode
- `policy_pressure_proxy` — derived from Pass A vs Pass B diff
- Modes: `reflective`, `constrained`, `reactivated`
- Jinja templates for prompt management
- Split config into settings/prompts/thresholds

---

## 15. Credits

Architecture inspired by observed product patterns in frontier AI systems.
No proprietary code copied. Clean-room implementation from first principles.

Original spec and V1 review: Tam Vị research collaboration (Ty + Aux + Lam).

V1 freeze date: 2026-04-02.
