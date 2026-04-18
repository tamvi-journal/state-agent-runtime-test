# Technical Analysis Worker
### Bridge spec between skill, worker, tool, gate, verification, and brain

## Purpose

This document defines how the **technical analysis skill** should connect to the runtime.

It exists to prevent one very common architecture mistake:

> putting domain method, raw execution, and final interpretation into one blob.

This file describes the correct separation for technical analysis inside the thin harness.

---

# 1. Layer roles

## Skill
**File:** `skills/technical-analysis.md`

Role:
- procedural method
- analysis order
- domain discipline
- interpretation guardrails
- stop conditions

Question it answers:
> How should technical analysis be approached?

The skill should guide:
- what to inspect first
- what to inspect second
- how to avoid overclaiming
- when to hold open

The skill does **not** execute.

---

## Tool
**Suggested file:** `src/tools/market_data_tool.py`  
**Future tools:** `src/tools/technical_analysis_tool.py`

Role:
- bounded execution
- data loading
- data parsing
- indicator computation if needed
- structured raw result output

Question it answers:
> What narrow action can be executed safely?

Examples:
- load OHLCV from CSV
- compute moving averages
- compute RSI / KDJ / MACD
- return normalized chart data

The tool does **not** produce final user-facing analysis.

---

## Worker
**Suggested file:** `src/workers/technical_analysis_worker.py`

Role:
- domain task logic
- apply the skill method to tool outputs
- package evidence
- attach assumptions
- attach warnings
- assign bounded confidence
- prepare payload for brain synthesis

Question it answers:
> Given data and method, what technical-analysis evidence package should be handed to the brain?

The worker is where:
- structure read
- volume interpretation
- indicator confirmation
- invalidation logic
- uncertainty handling

should be shaped.

The worker does **not** own final user-facing truth.

---

## Gate
**File:** `src/gate/execution_gate.py`

Role:
- permission boundary before market-data load or analysis execution
- allow / sandbox_only / needs_approval / deny

Question it answers:
> Is this technical-analysis action path allowed?

Gate should decide whether the runtime may:
- load price data
- run bounded technical computation
- use local file inputs
- escalate to any future higher-risk tool path

The gate does **not** decide the analysis conclusion.

---

## Verification
**File:** `src/verification/verification_loop.py`

Role:
- distinguish intended action, executed action, observed outcome
- prevent fake completion
- keep analysis claims grounded in actual loaded data

Question it answers:
> What actually happened, and is the runtime allowed to treat the analysis input as verified enough?

Verification is especially important when:
- data load may fail
- file path may be wrong
- indicators may be computed on incomplete input
- benchmark/sector context may be missing

---

## Brain
**File:** `src/brain/main_brain.py`

Role:
- final synthesis authority
- convert evidence package into the user-facing explanation
- preserve uncertainty honestly
- keep the analysis readable

Question it answers:
> Given the verified evidence package, what should the final answer say?

The brain may:
- summarize
- compare scenarios
- explain structure cleanly
- communicate uncertainty

The brain must not pretend the worker/tool proved more than they actually did.

---

# 2. Runtime flow for technical analysis

Correct runtime order:

```text
user asks for technical analysis
→ runtime identifies finance / TA task
→ technical-analysis skill is selected
→ gate approves bounded data/analysis path
→ market data tool loads structured data
→ optional technical analysis tool computes indicators
→ technical analysis worker applies method from skill
→ verification records what data was actually loaded and what was computed
→ main brain synthesizes final analysis
→ baton carries open loops / next hint
```

This is the intended shape.

---

# 3. Minimal current version

For the current thin harness, do **not** overbuild yet.

A minimal technical-analysis path can be:

```text
technical-analysis skill
→ market_data_tool
→ technical_analysis_worker
→ verification
→ main brain
```

That means:
- the skill provides method
- the market data tool provides normalized OHLCV input
- the worker performs the actual TA read
- verification confirms the data path
- the brain writes the final explanation

This is enough for v0.1.

---

# 4. Recommended files

## Current minimum
```text
skills/
  technical-analysis.md

src/tools/
  contracts.py
  market_data_tool.py

src/workers/
  technical_analysis_worker.py
```

## Future expansion
```text
src/tools/
  technical_analysis_tool.py
```

Only add `technical_analysis_tool.py` when technical computations become real enough to justify a separate bounded action unit.

Do not create it just for symmetry.

---

# 5. Worker inputs

The technical analysis worker should ideally receive:

- ticker or symbol
- timeframe
- normalized OHLCV data
- optional benchmark context
- optional sector context
- active skill or skill summary
- current monitor summary if relevant
- verification record for the loaded data

### Why
This keeps worker behavior tied to:
- actual data
- actual method
- actual runtime state

instead of hidden assumptions.

---

# 6. Worker output contract

The technical analysis worker should output an **evidence package**, not a final verdict blob.

Suggested shape:

```json
{
  "task_type": "technical_analysis",
  "symbol": "",
  "timeframe": "",
  "data_status": "loaded|partial|missing",
  "structure_read": "",
  "volume_read": "",
  "indicator_read": {
    "rsi": "",
    "kdj": "",
    "macd": "",
    "moving_averages": ""
  },
  "alignment_status": "bullish|bearish|mixed|range|unresolved",
  "invalidation_condition": "",
  "assumptions": [],
  "warnings": [],
  "confidence": 0.0,
  "verification_status": ""
}
```

### Why this shape
It forces the worker to separate:
- structure
- volume
- indicators
- uncertainty
- invalidation

instead of compressing everything into one confident paragraph.

---

# 7. Tool responsibilities

## MarketDataTool
Owns:
- file existence check
- CSV loading
- row parsing
- numeric normalization
- bounded raw data return
- data integrity warnings

Does **not** own:
- chart interpretation
- bullish/bearish thesis
- narrative explanation

---

## Future TechnicalAnalysisTool
If created later, it may own:
- moving average computation
- RSI computation
- KDJ computation
- MACD computation
- rolling volume statistics
- simple support/resistance helper output

It still should **not** own:
- final directional claim
- holistic narrative interpretation
- user-facing conclusion

---

# 8. Skill responsibilities

The technical-analysis skill should determine **method order**.

That means it tells the worker:

1. establish timeframe/context
2. read structure first
3. read volume second
4. use indicators third
5. compare alignment/conflict
6. frame risk and invalidation
7. stop if evidence is weak

This is the most important contribution of the skill.

Without the skill, the worker may drift into:
- indicator-first analysis
- overclaiming
- inconsistent ordering
- messy chart commentary

---

# 9. Gate posture for technical analysis

Typical low-risk technical analysis using local approved market data should usually be:

- `allow`
or
- `sandbox_only`

depending on runtime policy.

### Gate should pay attention to:
- file access scope
- whether data source is approved
- whether shell/network calls are involved
- whether the worker is trying to bypass bounded data load

### Gate should not decide:
- whether the chart is bullish
- whether RSI matters more than MACD
- whether the thesis is good

That belongs downstream.

---

# 10. Verification posture for technical analysis

Verification should answer:

- Was market data actually loaded?
- For which symbol?
- For which timeframe?
- Was the dataset partial or complete enough?
- Were indicator values computed from the actual loaded dataset?
- Is benchmark/sector context missing?
- Is the final analysis stronger than the evidence allows?

### Common verification statuses
- `passed` → data load and computation path are valid enough for the claimed scope
- `partial` → enough for a limited read, not a firm call
- `unknown` → load/computation path uncertain
- `failed` → data path broken or invalid

### Important
Technical analysis often tempts the runtime into saying more than the data supports.

Verification exists to stop this.

---

# 11. Brain synthesis rules

When the brain receives a technical-analysis evidence package, it should:

## Do
- explain timeframe
- summarize structure first
- mention volume confirmation/conflict
- mention indicators as secondary evidence
- clearly state whether signals align or conflict
- include invalidation if relevant
- preserve uncertainty honestly

## Do not
- invent confidence
- flatten mixed signals into one clean thesis
- say “buy now” unless the architecture and evidence are designed for that strength
- hide missing data under fluent language

### Practical rule
> Brain speaks the analysis, but only at the strength justified by verified worker evidence.

---

# 12. Baton behavior for technical analysis

A technical-analysis turn may emit a baton like:

```json
{
  "task_focus": "technical analysis for MBB daily timeframe",
  "active_mode": "analysis",
  "open_loops": [
    "benchmark comparison not loaded",
    "sector context still missing"
  ],
  "verification_status": "partial",
  "monitor_summary": "mixed signals, avoid fake closure",
  "next_hint": "load benchmark/sector context before stronger directional conclusion"
}
```

### Why this matters
It prevents the next turn from behaving as if:
- the job is fully done
- the conclusion is already settled
- the missing context never mattered

---

# 13. Failure modes to avoid

## Failure A — Tool/worker collapse
Raw data loading and full interpretation are fused into one class.

Result:
- bad boundaries
- weak verification
- hard debugging

---

## Failure B — Indicator-first worker
Worker jumps to RSI/MACD before reading structure.

Result:
- shallow or noisy analysis
- overclaiming from secondary signals

---

## Failure C — Worker as final truth speaker
Worker returns one polished narrative instead of an evidence package.

Result:
- brain loses synthesis discipline
- uncertainty gets hidden early

---

## Failure D — Fake completion
Data loaded partially, but analysis is phrased as fully verified.

Result:
- runtime sounds confident on weak footing

---

## Failure E — Decorative extra tool
A `technical_analysis_tool.py` is created before real technical computation exists.

Result:
- architecture inflation
- fake cleanliness
- more files, no more clarity

---

# 14. Recommended build phases

## Phase 1
- keep `technical-analysis.md`
- keep `market_data_tool.py`
- create `technical_analysis_worker.py`
- route brain synthesis from worker evidence

## Phase 2
- strengthen worker output schema
- add technical-analysis-specific verification checks
- improve baton handling for partial reads

## Phase 3
- add `technical_analysis_tool.py` only if indicator computation becomes a real bounded execution layer worth separating

## Phase 4
- optionally add benchmark/sector comparison tools and related worker enhancements

---

# 15. One-line summary

> **The technical-analysis skill defines the method, the tool loads the data, the worker turns data into disciplined evidence, verification keeps the read honest, and the brain is the only layer allowed to turn that evidence into the final chart analysis.**
