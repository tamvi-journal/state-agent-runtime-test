# Tool Roadmap Spec v0.1
### Capability roadmap for a thin single-agent runtime

## Purpose

This document defines a practical roadmap for the `tools/` layer in the agent runtime.

The goal is not to add every possible tool immediately.
The goal is:

> **to grow the tool layer in a disciplined order, so the runtime gains real capability without collapsing its boundaries.**

This roadmap assumes the runtime already has:
- a **main brain** for final synthesis
- a **monitor** for drift / ambiguity / fake progress / mode decay
- a **gate** for permission and runtime boundaries
- a **verification loop** for truth after action
- **state + baton handoff** for continuity
- **workers** for domain-level task logic

In that stack:
- **tools** are bounded action units
- **workers** are domain-level orchestrators
- **brain** remains the final authority

---

# 1. Core principle

> **A tool is not a personality, not a worker, and not a brain.**
> **A tool is one bounded capability with a clear execution surface.**

A tool should:
- take a structured request
- perform one bounded action or transformation
- return structured output
- stay narrow enough for gate + verification to reason about it

A tool should **not**:
- decide the final answer
- absorb domain strategy that belongs in a worker
- silently widen its own permissions
- mutate state outside approved paths

---

# 2. Why a `tools/` layer is needed

Without a dedicated `tools/` layer, the runtime tends to blur roles:

- workers hide raw execution logic inline
- gate boundaries become harder to read
- verification has a weaker grip on what actually ran
- domain logic and execution logic become entangled
- future expansion becomes messy

A clear `tools/` layer fixes this by making the runtime read like this:

```text
brain
→ runtime decides action intent
→ gate checks permission
→ worker orchestrates task
→ tool performs bounded action
→ verification checks observed outcome
→ brain synthesizes final answer
```

That separation is the whole point.

---

# 3. Role boundaries

## 3.1 Tools
Tools are bounded execution units.

Examples:
- read a CSV
- fetch market data from an approved source
- run a sandboxed shell command
- write a file inside an approved directory
- compute a technical indicator from verified inputs

## 3.2 Workers
Workers use one or more tools to complete a domain task.

Examples:
- market-data worker
- workflow-builder worker
- app-builder worker
- creative-content worker
- fundamentals-analysis worker

Workers may:
- choose sequence
- combine tool outputs
- add warnings / assumptions / confidence framing
- prepare evidence packages for the brain

Workers should **not** become hidden raw execution engines.

## 3.3 Main Brain
The brain remains synthesis authority.

It decides:
- what to say outwardly
- how to interpret tool/worker evidence
- whether truth is strong enough for a firm claim
- whether the result is complete, tentative, or open

---

# 4. Tool design laws

## Law 1 — Narrow action surface
Each tool should do one class of thing clearly.

## Law 2 — Explicit contract
Each tool should accept structured input and return structured output.

## Law 3 — Gate before action
A tool must not become a permission boundary itself.
The gate decides whether it may run.

## Law 4 — Verification after action
A tool may return execution output, but it does not certify reality by itself.
Verification still decides whether the intended result was actually observed.

## Law 5 — No fake completion
A tool success value is not the same as task completion.

## Law 6 — No silent scope creep
A tool must not quietly evolve from narrow action into a hidden orchestration layer.

---

# 5. Minimal contract layer

Recommended starter contract file:

```text
src/tools/contracts.py
```

Suggested contents:
- `ToolRequest`
- `ToolResult`
- optional `ToolExecutionMeta`
- bounded error/result shape

## Example contract shape

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolRequest:
    tool_name: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResult:
    tool_name: str
    action: str
    ok: bool
    output: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
```

This should remain small.
Do not build a framework too early.

---

# 6. Growth strategy

The tool roadmap should grow in layers.

## Phase 1 — One real tool
Build only the tool the active harness already truly needs.

Current recommended file:

```text
src/tools/
  contracts.py
  market_data_tool.py
```

This proves the boundary.

## Phase 2 — Core execution tools
Add foundational tools used across many domains.

## Phase 3 — Builder tools
Add tools for code, apps, workflows, and local automation.

## Phase 4 — Finance tools
Add tools for market data, technical analysis, fundamentals, portfolio analysis, and coin/on-chain work.

## Phase 5 — Creative and research tools
Add prompt/content tools, creative generation helpers, retrieval, comparison, and structured note tools.

---

# 7. Tool categories

The roadmap is grouped into six tool families.

---

## 7.1 Core execution tools
These are the runtime hands.

### Files
```text
src/tools/
  filesystem_tool.py
  shell_tool.py
  http_tool.py
  python_tool.py
```

### Roles

#### `filesystem_tool.py`
Bounded file operations.

Examples:
- read file
- write file in approved path
- list tree
- copy/move file
- create directory

Why it matters:
- app building
- workflow editing
- project mutation
- content generation pipelines

#### `shell_tool.py`
Bounded shell execution.

Examples:
- run tests
- run build commands
- inspect environment
- execute safe scripts in sandbox

Why it matters:
- local automation
- developer workflows
- debugging

#### `http_tool.py`
Bounded network/API access.

Examples:
- fetch approved API resource
- call market endpoint
- retrieve metadata
- query internal service

Why it matters:
- market/fundamental data
- web lookup
- automation integrations

#### `python_tool.py`
Sandboxed Python execution for transformations.

Examples:
- compute indicators
- reshape tables
- run small analytics
- generate derived outputs

Why it matters:
- finance
- reporting
- workflow transformations
- structured analysis

---

## 7.2 Builder / developer tools
These are for app, code, workflow, and repo construction.

### Files
```text
src/tools/
  git_tool.py
  package_tool.py
  test_runner_tool.py
  workflow_tool.py
  browser_preview_tool.py
```

### Roles

#### `git_tool.py`
Repo-aware operations.

Examples:
- status
- diff
- branch checks
- staged change summary
- commit helper (approval-gated)

#### `package_tool.py`
Package/environment operations.

Examples:
- inspect installed package
- check version
- install/update in approved scope

#### `test_runner_tool.py`
Run bounded test/build flows.

Examples:
- `pytest`
- `npm test`
- `npm run build`
- smoke tests

#### `workflow_tool.py`
Generate/edit workflow specs.

Examples:
- node graph edits
- workflow JSON shaping
- validation of flow structure

#### `browser_preview_tool.py`
Optional preview surface.

Examples:
- open preview metadata
- capture build preview info
- surface app route checks

---

## 7.3 Automation / orchestration tools
These are for agentic workflow construction.

### Files
```text
src/tools/
  n8n_tool.py
  openclaw_tool.py
  scheduler_tool.py
  trigger_tool.py
```

### Roles

#### `n8n_tool.py`
Read/write/validate n8n workflows.

#### `openclaw_tool.py`
Thin OpenClaw-specific adapter actions.

#### `scheduler_tool.py`
Create or inspect schedules/triggers.

#### `trigger_tool.py`
Handle event/trigger spec translation.

Why this family matters:
- workflow authoring
- automation design
- orchestration experiments
- low-code agent systems

---

## 7.4 Creative tools
These support content and concept generation.

### Files
```text
src/tools/
  prompt_tool.py
  image_prompt_tool.py
  music_prompt_tool.py
  storyboard_tool.py
  content_tool.py
```

### Roles

#### `prompt_tool.py`
Prompt drafting/refinement across domains.

#### `image_prompt_tool.py`
Structured image prompt generation.

#### `music_prompt_tool.py`
Structured music/Suno-style prompt generation.

#### `storyboard_tool.py`
Scene sequence / visual narrative scaffolding.

#### `content_tool.py`
Article/post/caption/script generation helpers.

Why this family matters:
- creative ideation
- marketing content
- design references
- branding systems

---

## 7.5 Finance / market tools
These are the most important domain tools for a finance-focused agent.

### Files
```text
src/tools/
  market_data_tool.py
  technical_analysis_tool.py
  fundamentals_tool.py
  screener_tool.py
  portfolio_tool.py
  onchain_tool.py
```

### Roles

#### `market_data_tool.py`
Load and normalize OHLCV / benchmark / ticker data.

Examples:
- CSV load
- API fetch
- benchmark merge
- ticker/timeframe normalization

#### `technical_analysis_tool.py`
Indicator and price-structure calculations.

Examples:
- RSI
- KDJ
- MACD / EMACD
- MA / EMA
- volume behavior
- relative strength inputs

#### `fundamentals_tool.py`
Basic fundamental and valuation transforms.

Examples:
- EPS
- revenue growth
- margin trends
- PE/PB/valuation summary
- filing normalization

#### `screener_tool.py`
Rule-based filtering.

Examples:
- sector/ticker filters
- momentum screens
- liquidity filters
- valuation screens

#### `portfolio_tool.py`
Portfolio exposure and risk summaries.

Examples:
- current holdings summary
- concentration view
- sector allocation
- scenario notes

#### `onchain_tool.py`
Coin / crypto / on-chain metrics.

Examples:
- exchange flow
- holder metrics
- supply movement
- on-chain trend inputs

### Why this family matters
It lets the agent do more than chat about markets.
It gives the runtime bounded financial execution surfaces that workers can orchestrate.

---

## 7.6 Research / knowledge tools
These are for evidence gathering and synthesis support.

### Files
```text
src/tools/
  retrieval_tool.py
  document_tool.py
  comparison_tool.py
  note_tool.py
```

### Roles

#### `retrieval_tool.py`
Search/fetch across approved sources.

#### `document_tool.py`
Parse structured docs.

Examples:
- markdown
- csv
- json
- plain text

#### `comparison_tool.py`
Compare multiple sources/alternatives.

#### `note_tool.py`
Produce structured notes or evidence summaries.

Why this family matters:
- research
- analysis
- report generation
- multi-source comparison

---

# 8. Recommended implementation order

Do not build every tool family at once.

## Recommended order

### Step 1 — prove the tool boundary
- `contracts.py`
- `market_data_tool.py`

### Step 2 — add core execution capability
- `filesystem_tool.py`
- `http_tool.py`
- `python_tool.py`

### Step 3 — add builder capability
- `workflow_tool.py`
- `test_runner_tool.py`
- optionally `git_tool.py`

### Step 4 — add finance depth
- `technical_analysis_tool.py`
- `fundamentals_tool.py`
- `screener_tool.py`
- `portfolio_tool.py`
- `onchain_tool.py`

### Step 5 — add creative and research breadth
- `prompt_tool.py`
- `image_prompt_tool.py`
- `content_tool.py`
- `retrieval_tool.py`
- `comparison_tool.py`

This order preserves discipline.

---

# 9. What should not be a tool

The following do **not** belong in `tools/`:

- final answer synthesis
- mode inference
- monitor scoring
- gate policy
- verification truth judgment
- long-running memory decisions
- unresolved disagreement management
- broad domain strategy

Those belong elsewhere:
- brain
- monitor
- gate
- verification
- state
- workers

---

# 10. Anti-patterns

## Anti-pattern A — decorative tools
Creating files like `shell_tool.py` or `filesystem_tool.py` before the runtime actually uses them.

## Anti-pattern B — worker-tool blur
Keeping raw file/network/shell logic hidden inside workers forever.

## Anti-pattern C — tool becomes brain
Letting a tool decide conclusions, strategy, or final claims.

## Anti-pattern D — gate collapse
Letting tools self-authorize instead of being gated.

## Anti-pattern E — verification collapse
Treating tool success as proof of observed reality.

## Anti-pattern F — too much framework too early
Building a plugin system before the runtime has even stabilized around 2–4 real tools.

---

# 11. Minimal near-term recommendation for this repo

For the current thin harness, the recommended immediate target is:

```text
src/tools/
  contracts.py
  market_data_tool.py
```

That is enough to:
- prove the architecture boundary
- keep the repo honest
- prevent decorative expansion
- prepare for future builder / creative / finance tools later

---

# 12. Long-term stack sentence

> **Tools are the bounded hands of the runtime. Workers decide how to use those hands. The brain decides what the whole action means. Gate controls permission. Verification checks reality.**

That is the architecture.

---

# One-line version

> **Add tools in the order real capability appears: first one living tool, then core execution, then builder, finance, creative, and research families — without letting tools swallow workers, gate, or brain.**
