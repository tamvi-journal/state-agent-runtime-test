# Skill: Macro Sector Mapping

---
skill_id: macro_sector_mapping
title: Macro Sector Mapping
domain: market_radar
use_when:
  - translating normalized macro signals into Vietnam sector implications
  - building or reviewing Engine A macro-to-sector bias output
  - attaching watch stocks, confidence, and decay to macro themes
avoid_when:
  - only raw headlines exist and no normalized macro signal has been produced
  - the task is real-flow confirmation or stock setup scoring
required_tools:
  - config_loader
optional_tools:
  - market_data_tool
tags:
  - market_radar
  - engine_a
  - macro
  - sector
  - mapping
---

## Purpose

Use this skill when the task is to convert normalized global macro signals into Vietnam sector implications for Engine A.

This skill exists to prevent:
- narrative-only sector calls
- dropping negative sector implications while keeping only the bullish story
- inventing sectors or watch stocks outside the canonical trigger map
- overstating confidence when multiple macro signals conflict

---

## Use when

Activate this skill when the task is to:
- read `global_signals`
- match signals to canonical macro triggers
- create `vn_sector_bias`
- attach sector direction, confidence, decay, and watch stocks
- preserve ambiguity when multiple triggers interact

---

## Do not use when

Do not use this skill when:
- the input is still a raw headline list rather than normalized macro signals
- the task is to verify real VN sector flow
- the task is to score individual stock setups
- the task is to override the trigger map by intuition alone

---

## Inputs expected

Minimum useful inputs:
- normalized macro signals shaped like [sample_morning_macro_scan.json](D:/husband-agent-runtime-test/samples/sample_morning_macro_scan.json)
- canonical trigger map in [macro_sector_map_v1.json](D:/husband-agent-runtime-test/config/macro_sector_map_v1.json)

Useful extras:
- prior active trigger history
- decay remaining from earlier runs
- sector-level conflict notes from the same session

---

## Method

### Step 1 — Start from normalized signals, not raw news
Require each signal to already have:
- a stable `signal_id`
- a theme
- a direction
- a strength score
- a confidence level
- a time horizon

If that normalization has not happened, stop and hand back the need for a macro-scan pass first.

### Step 2 — Match to the canonical trigger map
Use [macro_sector_map_v1.json](D:/husband-agent-runtime-test/config/macro_sector_map_v1.json) as the canonical rule source.

For each signal:
- identify the most plausible trigger key
- prefer an exact conceptual match over a vague analogy
- keep unmatched signals visible for manual review rather than forcing them into the nearest story

Do not improvise new sectors just because the narrative sounds plausible.

### Step 3 — Expand both positive and negative implications
For a matched trigger:
- emit sector-bias entries for `vn_sectors_positive`
- emit sector-bias entries for `vn_sectors_negative`
- preserve the direction separately for each sector

Do not keep only the attractive side of the map. Many triggers matter because they help one cluster and pressure another.

### Step 4 — Attach watch stocks, confidence, and decay from the map
For each sector-bias entry:
- attach watch stocks from the mapped sector list
- carry the map confidence as the base confidence
- carry `decay_days` as the initial time horizon for the bias
- keep the trigger notes available as explanation, not as the whole judgment

Treat the config as the canonical rule source. Do not duplicate its tables into the output.

### Step 5 — Merge same-sector effects conservatively
If multiple signals hit the same sector:
- keep supporting trigger ids
- preserve opposing pressures if directions conflict
- prefer conservative confidence when signals are mixed
- avoid turning several medium signals into fake-high certainty just because they share a sector

The output should stay evidence-shaped, not prophecy-shaped.

### Step 6 — Preserve conflict honestly
If one trigger is positive for a sector and another is negative:
- keep the conflict visible
- note that the sector bias is mixed or contested
- avoid flattening the result into one clean directional claim

This skill should preserve ambiguity, not delete it.

### Step 7 — Emit runtime-friendly bias objects
Shape the result like [sample_macro_to_vn_sector_map.json](D:/husband-agent-runtime-test/samples/sample_macro_to_vn_sector_map.json):
- one bias object per sector implication
- include the trigger signal id
- include sector, direction, strength, confidence, decay, reason, and watch stocks

This skill defines the method for producing those objects. It does not execute the workflow itself.

---

## Failure modes

Avoid:
- mapping from raw headlines without normalized signal fields
- inventing sectors or watch lists outside the config
- keeping only positive implications and dropping negative ones
- ignoring `decay_days`
- treating config confidence as certainty rather than bounded confidence
- collapsing conflicting triggers into one neat story
- forcing every macro signal to match a trigger

---

## Tool hints

Usually relevant:
- a config-loading tool or file reader for [macro_sector_map_v1.json](D:/husband-agent-runtime-test/config/macro_sector_map_v1.json)

Sometimes relevant:
- a structured macro-signal loader for [sample_morning_macro_scan.json](D:/husband-agent-runtime-test/samples/sample_morning_macro_scan.json)-style input

This skill does not execute the mapping by itself.

---

## Output expectations

A good output should contain:

1. one bias object per sector implication, not one vague paragraph
2. `trigger_signal_id`
3. `sector`
4. `direction`
5. `strength_score`
6. `confidence`
7. `decay_days`
8. `reason`
9. `watch_stocks`
10. concise notes when conflict or ambiguity is present

The output should look like Engine A sector-bias evidence, not a final market opinion.

---

## Stop conditions

Hold open or abstain when:
- no normalized macro signal is available
- no trigger match is defensible
- the signal is too vague to support sector translation
- multiple triggers conflict and no honest conservative merge is possible
- the user asks for certainty stronger than the mapped evidence supports

If the mapping is weak, say:
> partial macro-sector mapping only

---

## One-line summary

> Map normalized macro signals through the canonical trigger file, expand both positive and negative sector implications, and preserve conflict instead of forcing a clean story.
