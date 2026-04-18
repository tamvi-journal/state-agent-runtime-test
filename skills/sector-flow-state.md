# Skill: Sector Flow State

---
skill_id: sector_flow_state
title: Sector Flow State
domain: market_radar
use_when:
  - classifying Vietnam sectors into WATCH, ACTIVE, HOT, or WEAKENING
  - checking whether macro bias is confirmed by real sector flow
  - building or reviewing Engine A sector flow board output
avoid_when:
  - only macro narrative exists and no sector metrics are available
  - the task is stock-level candle or setup scoring
required_tools:
  - market_data_tool
  - config_loader
optional_tools:
  - breadth_or_basket_loader
tags:
  - market_radar
  - engine_a
  - sector
  - flow
  - state
---

## Purpose

Use this skill when the task is to translate sector-level market behavior into disciplined sector states for Engine A.

This skill exists to prevent:
- treating macro narrative as proof of sector strength
- forcing alignment when flow contradicts the story
- calling a sector HOT too easily
- overreacting to one session without context

---

## Use when

Activate this skill when the task is to:
- read sector metrics
- compare macro bias with real market confirmation
- classify sectors into `WATCH`, `ACTIVE`, `HOT`, or `WEAKENING`
- surface state transitions and caution overlays

---

## Do not use when

Do not use this skill when:
- only headlines or macro bias exist
- sector metrics such as RS, breadth, or volume regime are missing
- the task is to rank individual stocks inside a sector
- the task is to override state rules with pure narrative conviction

---

## Inputs expected

Minimum useful inputs:
- sector universe from [sector_universe_v1.json](D:/husband-agent-runtime-test/config/sector_universe_v1.json)
- sector-state rules from [sector_state_rules_v1.json](D:/husband-agent-runtime-test/config/sector_state_rules_v1.json)
- benchmark context such as VNIndex
- sector metrics shaped like [sample_sector_flow_output.json](D:/husband-agent-runtime-test/samples/sample_sector_flow_output.json)

Useful extras:
- prior session state
- macro sector bias from the mapping layer
- hot-streak duration for late-entry overlay

---

## Method

### Step 1 — Lock the sector frame before judging state
Use the enabled sector universe from [sector_universe_v1.json](D:/husband-agent-runtime-test/config/sector_universe_v1.json).

For each sector:
- use the representative basket consistently
- keep benchmark comparison consistent
- avoid changing the basket mid-read just to fit the thesis

### Step 2 — Read actual flow metrics first
Before assigning a state, require the core metrics defined by the spec and rules:
- `rs_score`
- `breadth_score`
- `volume_ratio_vs_ma20`
- `up_down_ratio`
- `leader_count`
- `breakout_count`
- `breakdown_count`

Macro alignment is an input, but not a substitute for these metrics.

### Step 3 — Compare narrative bias against real flow
If macro bias exists:
- check whether the sector metrics confirm it
- keep `macro_alignment = true` only when the flow and story are genuinely aligned
- preserve conflict when narrative bias exists but price/volume/breadth do not confirm it

Do not force macro and flow to match when they clearly disagree.

### Step 4 — Apply classification in the canonical order
Use [sector_state_rules_v1.json](D:/husband-agent-runtime-test/config/sector_state_rules_v1.json) as the canonical rule source.

Evaluate states in this order:
1. `HOT`
2. `ACTIVE`
3. `WATCH`
4. `WEAKENING`

This matters because the rules intentionally make `HOT` harder than `ACTIVE`, and `WEAKENING` can override a weak watch-style reading when a formerly strong sector is losing confirmation.

### Step 5 — Use tie-break notes and prior-state context
When the sector sits near multiple states:
- prefer `WEAKENING` over `WATCH` if the sector was previously `ACTIVE` or `HOT` and is now deteriorating
- keep a near-HOT sector at `ACTIVE` if breakout breadth is still too thin
- use macro alignment as support, not override

Treat prior state as context, not destiny.

### Step 6 — Add caution overlays without rewriting the state
If the sector is still valid but stretched:
- attach overlays such as `late_entry_risk`
- keep the state unchanged if the canonical rules still support it

An overlay is a caution flag, not a hidden downgrade.

### Step 7 — Emit a state board, not a sector narrative essay
Shape the output like [sample_sector_flow_output.json](D:/husband-agent-runtime-test/samples/sample_sector_flow_output.json):
- `sector`
- `state`
- `direction`
- core metrics
- `macro_alignment`
- `flags`

The goal is a disciplined sector-flow board, not a persuasive sector story.

---

## Failure modes

Avoid:
- calling a sector strong because the macro story sounds attractive
- ignoring weak breadth or weak RS because one leader looks good
- using one green day as proof of confirmation
- promoting too many sectors to `HOT`
- flattening macro-vs-flow conflict into fake clarity
- forgetting that `WEAKENING` often depends on deterioration from a previously stronger state

---

## Tool hints

Usually relevant:
- a market-data or breadth loader for sector and benchmark metrics
- a config loader for [sector_state_rules_v1.json](D:/husband-agent-runtime-test/config/sector_state_rules_v1.json) and [sector_universe_v1.json](D:/husband-agent-runtime-test/config/sector_universe_v1.json)

This skill does not execute sector-state computation by itself.

---

## Output expectations

A good output should contain:

1. sector key
2. assigned state
3. direction
4. RS, breadth, volume ratio, up/down ratio, leader, breakout, and breakdown metrics
5. macro-alignment status
6. flags or overlays when needed
7. concise conflict notes when narrative and flow diverge

The output should stay board-shaped and inspection-friendly.

---

## Stop conditions

Hold open or abstain when:
- benchmark context is missing
- representative sector basket is unavailable
- too many required metrics are missing
- macro bias is present but real flow data is not yet available
- the evidence is too thin to assign a state honestly

If the evidence is incomplete, say:
> partial sector-state read only

---

## One-line summary

> Read real sector flow first, apply the canonical state rules in order, and never let a good macro story override weak breadth, RS, or volume confirmation.
