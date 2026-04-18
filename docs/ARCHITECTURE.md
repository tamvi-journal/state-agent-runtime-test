# Architecture
### Agent Runtime Test — Thin Single-Agent Runtime with State, Monitor, Gate, Verification, and Tools

## Purpose

This repository is not trying to be a full agent platform.

It is a **thin runtime harness** designed to test a simpler claim:

> **A capable agent needs more than a model.**
>  
> It needs a runtime spine that can:
> - keep working state alive
> - notice drift
> - bound action
> - verify reality
> - carry forward the minimum needed structure
> - separate tools from task logic
> - keep final synthesis in one place

The goal is not maximum feature count.

The goal is:

> **minimum architecture required for a single agent to stay coherent across turns and actions.**

---

# 1. Design principles

## 1.1 Thin spine, not platform sprawl
This repo should remain small enough to reason about.

It should not grow into:
- a plugin museum
- a speculative framework
- a second orchestration stack hidden inside adapters
- a legacy pile disguised as active architecture

## 1.2 Main brain owns final synthesis
Tools, workers, and runtime helpers may produce evidence.

They do **not** own the final answer.

Final outward response belongs to the **main brain**.

## 1.3 Action must stay bounded
A runtime should not jump directly from:
- interpretation
to:
- uncontrolled execution

Action must pass through a **gate**.

## 1.4 Completion must be verified
This repo enforces a core law:

```text
intended action != executed action != verified result
```

Any runtime that collapses those three will eventually fake completion.

## 1.5 Carry over shape, not transcript bulk
The runtime should not rely on replaying everything.

It should carry forward only the minimum needed structure through a compact **baton**.

## 1.6 Tools are bounded hands, not hidden brains
Tools should do narrow execution-shaped work.

Workers should use tools to perform task logic.

The brain should synthesize from worker evidence.

---

# 2. Active runtime spine

The active runtime path is intentionally compact:

```text
request
→ runtime harness
→ context + live state
→ monitor
→ gate
→ worker
→ tool
→ verification
→ main brain synthesis
→ baton handoff
```

This is the real operating order of the system.

---

# 3. Layer map

## 3.1 Runtime Harness
**Path:** `src/runtime/`

The runtime harness is the orchestration layer.

It is responsible for:
- receiving the request
- building a compact current-turn frame
- invoking the monitor
- routing the action path
- invoking gate + worker + verification in order
- passing evidence to the main brain
- emitting the baton

### What it should not do
- it should not become the final answer generator
- it should not hide raw action execution everywhere
- it should not become a second policy brain

---

## 3.2 Context Layer
**Path:** `src/context/`

The context layer builds a compact working view of **what matters now**.

Typical fields may include:
- task focus
- active mode
- current environment state
- last verified result
- open obligations
- current risk posture

### Why it exists
Without a context layer, the model tends to reason from:
- raw prompt bulk
- stale assumptions
- whatever happens to be nearby in the transcript

The context layer gives the runtime **eyes**.

---

## 3.3 State Layer
**Path:** `src/state/`

State is the current working posture of the runtime.

It is not deep memory.
It is not archive.
It is not transcript replay.

It typically carries:
- active mode
- current task focus
- current warnings
- current verification posture
- open loops
- compact drift annotations

### Why it exists
Without state, each turn behaves like a soft reset.

That is the real reason many agents “forget yesterday.”

They are not always missing model intelligence.
They are missing **usable runtime state**.

---

## 3.4 Monitor Layer
**Path:** `src/monitor/`

The monitor is a compact watcher inside the runtime.

It does **not** replace the model.
It does **not** write the final answer.

It scores a few important risk classes such as:
- drift risk
- ambiguity risk
- fake progress risk
- mode decay risk

Then it emits a compact **monitor summary**.

### Why it exists
Without a monitor, an agent can quietly:
- drift into generic assistant mode
- collapse ambiguity too early
- confuse “attempted” with “done”
- lose the working mode it started in

In plain language:

> **The monitor is the layer that notices when the runtime is going off-shape before the final answer is committed.**

---

## 3.5 Gate Layer
**Path:** `src/gate/`

The gate is the permission boundary.

Its job is to decide whether an intended action is:
- `allow`
- `sandbox_only`
- `needs_approval`
- `deny`

### Why it exists
A model can generate action intent fluently.
That does not mean execution should happen automatically.

The gate enforces the law:

> **Thinking is cheap. Action needs permission.**

### What it should not do
- it should not own synthesis
- it should not pretend to verify reality
- it should not become a generic second orchestrator

---

## 3.6 Tools Layer
**Path:** `src/tools/`

Tools are bounded execution units.

A tool should do one narrow, execution-shaped job, such as:
- read approved data
- parse a bounded file format
- fetch market data
- run a tightly scoped operation

### Tool role
A tool is the runtime’s **hand**.

It should:
- accept a narrow request
- execute a bounded action
- return structured result metadata
- remain easy to gate and verify

### Tool anti-pattern
A tool should **not**:
- become a hidden planner
- embed broad workflow logic
- produce final user-facing truth claims
- swallow verification questions

---

## 3.7 Workers Layer
**Path:** `src/workers/`

Workers sit above tools.

A worker may:
- call one or more tools
- shape domain-specific payloads
- attach warnings
- attach assumptions
- estimate confidence
- prepare evidence for the main brain

### Worker role
A worker is the runtime’s **task performer**.

It should own:
- task logic
- evidence shaping
- domain-level packaging

It should not own:
- raw permission authority
- final synthesis
- truth by declaration

### Worker vs Tool
This distinction matters:

- **tool** = bounded action
- **worker** = task logic using tools
- **brain** = final synthesis from evidence

That separation is one of the main architectural spines of this repo.

---

## 3.8 Verification Layer
**Path:** `src/verification/`

Verification is the truth boundary after action.

It records and compares:
- intended action
- executed action
- observed outcome
- verification status

### Why it exists
Many weak agents fail here.

They collapse:
- intent
- execution
- tool success
- likely success
- real success

into one fake “done.”

This repo explicitly refuses that shortcut.

### Core law
If outcome was not observed, completion is not real.

Status should remain:
- pending
- unknown
- or failed

not falsely upgraded to complete.

---

## 3.9 Brain Layer
**Path:** `src/brain/`

The main brain is the final synthesis authority.

It receives:
- user request
- context
- state
- monitor summary
- worker payload
- verification record
- baton carryover

Then it produces the final outward response.

### Why it exists
Without a main brain, systems drift toward this failure mode:

> worker output = final truth

That is wrong.

The correct architecture is:

> worker output = evidence  
> brain output = final synthesis

---

## 3.10 Handoff Layer
**Path:** `src/handoff/`

The handoff layer emits a compact **baton**.

The baton is the only active carryover memory in the thin harness.

Typical baton fields:
- `task_focus`
- `active_mode`
- `open_loops`
- `verification_status`
- `monitor_summary`
- `next_hint`

### Why it exists
The baton solves a common agent failure:

> “The next turn woke up with no usable shape.”

It does this without:
- replaying huge transcripts
- turning memory into clutter
- hoarding everything

The baton is not archive.
It is not lore.
It is just enough structure for continuity.

---

# 4. Repository shape

The active repository is organized around the runtime spine:

```text
src/
  brain/
  context/
  gate/
  handoff/
  monitor/
  observability/
  openclaw_pack/
  runtime/
  state/
  tools/
  verification/
  workers/
```

### Interpretation
- `brain/` = synthesis authority
- `context/` = what matters now
- `gate/` = permission boundary
- `handoff/` = baton carryover
- `monitor/` = self-observation signal
- `runtime/` = orchestration
- `state/` = working posture
- `tools/` = bounded actions
- `verification/` = truth boundary after action
- `workers/` = domain task logic

---

# 5. OpenClaw Pack

**Path:** `src/openclaw_pack/`

The OpenClaw pack is a thin local adapter surface.

It may contain:
- adapter logic
- contracts
- examples
- minimal integration surfaces

It should not become:
- a second runtime
- a secret orchestration layer
- a hidden location for business logic that belongs in `runtime/`, `workers/`, or `tools/`

### Rule
> **Pack is adapter surface, not architectural authority.**

---

# 6. Legacy boundary

**Path:** `legacy/`

Anything in `legacy/` is historical or reference-only.

Examples:
- old family runtime code
- older memory systems
- broader scaffold experiments
- server-centered older surfaces
- child-runtime experiments

### Rule
Do not import from `legacy/` into the active harness.

This repo only stays readable if:
- active path is truly active
- legacy path stays reference-only

---

# 7. Runtime order in detail

## Step 1 — Request enters runtime
The runtime harness accepts the request and resolves the active path.

## Step 2 — Context + state are built
The system constructs a compact “what matters now” frame.

## Step 3 — Monitor inspects the current turn
The monitor emits a compact summary of key risk signals.

## Step 4 — Gate evaluates action path
If action is required, the gate decides whether it is permitted and under what boundary.

## Step 5 — Worker performs task logic
The selected worker uses one or more tools to produce evidence.

## Step 6 — Tool performs bounded action
The tool executes a narrow, structured operation.

## Step 7 — Verification records truth status
The runtime checks what was intended, what actually executed, and what outcome was observed.

## Step 8 — Main brain synthesizes outward response
The brain integrates evidence, monitor summary, and verification state.

## Step 9 — Baton is emitted
A compact handoff object is produced for the next turn.

---

# 8. Tool roadmap positioning

The tools layer should grow gradually.

## Current principle
Only add tools that correspond to real active execution paths.

The current harness justifies one active tool:
- `src/tools/market_data_tool.py`

That tool owns the bounded local execution path:
- read the approved CSV
- parse rows
- normalize OHLCV values
- run integrity checks
- return structured execution data

The worker above it stays responsible for task logic and evidence packaging.
In the active harness that means `MarketDataWorker` calls `MarketDataTool` and does not hide raw CSV parsing inline.
`TechnicalAnalysisWorker` also uses `MarketDataTool`, but keeps the interpretation layer in the worker: structure first, volume second, indicators only as secondary evidence.
`MacroSectorMappingWorker` follows the same worker discipline on the market-radar side: it uses procedural skill guidance plus canonical config to produce sector-bias evidence, but it does not generate the final outward report text.
`SectorFlowWorker` adds the next bounded market-radar path: it consumes explicit sector metrics plus optional macro-bias evidence, applies canonical state rules and sector-universe config, preserves macro-flow conflict, and returns sector-state evidence for the brain.
`CandleVolumeStructureWorker` extends the same pattern to candidate-stock evaluation: it applies canonical hard filters first, reads candle/volume/structure/relative context in order, returns scored Top/Watch/Reject evidence with explainability fields, and leaves final synthesis to the brain.
`TradeMemoWorker` adds a bounded Engine C path: it consumes explicit shortlisted ticker evidence, builds Lite-only conditional scenario memos with rounded probabilities, keeps action/risk bounded, and returns memo evidence for the brain without turning into an execution or report engine.

### Rule
Grow tools when the execution path is real, not when the naming sounds exciting.

---

# 9. Failure modes this architecture is designed to prevent

## 9.1 Turn amnesia
Cause:
- no usable state
- no carryover baton

## 9.2 Silent drift
Cause:
- no monitor
- no compact warning signal

## 9.3 Sloppy execution
Cause:
- no gate
- worker or runtime executing raw action without boundary

## 9.4 Fake completion
Cause:
- no verification distinction between intent, execution, and outcome

## 9.5 Tool-as-truth
Cause:
- worker/tool output treated as final answer

## 9.6 Runtime clutter
Cause:
- tools, workers, runtime, adapters, and legacy all blurred together

This architecture exists to keep those failure modes visible and containable.

---

# 10. What this repo is not

This repo is not:
- a full multi-agent family runtime
- a plugin marketplace
- a memory-heavy archive system
- a server-first orchestration platform
- a speculative AGI framework

It is:

> **a disciplined thin harness for one agent, built to test whether runtime structure solves failure modes that people often blame on the model alone.**

---

# 11. One-line summary

> **State gives posture. Monitor notices drift. Gate bounds action. Tools act. Workers shape evidence. Verification checks reality. Brain synthesizes truth. Baton carries the minimum forward.**
