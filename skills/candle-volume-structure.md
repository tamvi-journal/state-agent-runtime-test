# Skill: Candle Volume Structure

---
skill_id: candle_volume_structure
title: Candle Volume Structure
domain: market_radar
use_when:
  - scoring Engine A stock candidates into Top List or Watch List
  - reading candle, volume, structure, and relative context together
  - producing explainable setup scores without auto-buy language
avoid_when:
  - hard candidate filters have not run yet
  - no usable OHLCV history is available
  - the task is macro mapping or sector-state classification
required_tools:
  - market_data_tool
  - config_loader
optional_tools:
  - technical_analysis_tool
tags:
  - market_radar
  - engine_a
  - candle
  - volume
  - structure
  - scoring
---

## Purpose

Use this skill when the task is to evaluate already-filtered stock candidates with disciplined candle, volume, and structure logic for Engine A.

This skill exists to prevent:
- skipping hard filters and scoring junk anyway
- letting one pretty candle outrun a weak structure
- hiding risk behind a single final score
- turning Top List classification into disguised buy advice

---

## Use when

Activate this skill when the task is to:
- read candidate stocks after sector and hard-filter screening
- score setup quality
- separate Top List from Watch List
- produce explainable reasons such as `why_in`, `why_not_top`, and `risk_note`

---

## Do not use when

Do not use this skill when:
- the stock has not passed the hard candidate filter yet
- no OHLCV history exists
- the sector state is outside the allowed filter states
- the task is a general trading opinion instead of setup scoring

---

## Inputs expected

Minimum useful inputs:
- candidate stocks shaped like [sample_stock_candidates.json](D:/husband-agent-runtime-test/samples/sample_stock_candidates.json)
- hard filters from [hard_filter_rules_v1.json](D:/husband-agent-runtime-test/config/hard_filter_rules_v1.json)
- OHLCV history, ideally 60 to 150 sessions as described in the spec
- sector-state context

Useful extras:
- MA20 / MA50 / MA200
- RSI
- volume MA20
- benchmark or relative-strength context
- prior breakout or retest notes

---

## Method

### Step 1 — Confirm the candidate deserves deeper scoring
Before reading candles in detail, make sure the name already passed the hard filters governed by [hard_filter_rules_v1.json](D:/husband-agent-runtime-test/config/hard_filter_rules_v1.json).

That means checking things such as:
- allowed sector state
- minimum liquidity
- minimum RS
- no recent major breakdown
- no obvious near-breakdown risk

Do not use this skill to rescue names that should have been filtered out earlier.

### Step 2 — Read candle behavior first
Start with the immediate bar behavior:
- body size
- wick structure
- close quality
- range expansion or contraction
- whether the candle suggests momentum, quiet consolidation, reversal, or indecision

The candle is context, not a verdict.

### Step 3 — Read volume behavior second
Then ask whether participation confirms the candle:
- volume vs MA20
- volume vs recent sessions
- expansion or drying-up behavior
- whether price and volume align

If the price move looks good but participation is weak, lower conviction rather than forcing a clean bullish read.

### Step 4 — Read structure and location third
Only after candle and volume should you read structure:
- base quality
- breakout or retest status
- location near support or resistance
- above or below key moving averages
- whether the recent 3 to 10 bars show tightening, expansion, or damage

This is where you decide whether the setup is mature, early, loose, or fragile.

### Step 5 — Add relative context
Use sector and RS context as supporting evidence:
- sector state
- RS improving or weakening
- whether the stock behaves like a leader or laggard inside the sector

Relative context can strengthen or weaken the setup read, but it should not erase bad structure.

### Step 6 — Score the three required families
Produce:
- `trend_quality_score`
- `volume_confirmation_score`
- `setup_readiness_score`

Keep the score logic explainable. A score without reasons is not useful in this system.

### Step 7 — Write explainability outputs before classifying
Before deciding Top or Watch, populate:
- `why_in`
- `why_not_top`
- `risk_note`

The explainability fields are part of the method, not optional garnish.

Use short evidence phrases similar to the runtime samples when helpful:
- `strong_close`
- `volume_expansion`
- `needs_volume_confirmation`
- `still_under_resistance`

### Step 8 — Classify Top List versus Watch List
Use the scoring and explainability together.

Top List should mean:
- sector is already strong enough to matter
- structure quality is real
- candle and volume confirmation are present
- setup readiness is high enough that the chart is actionable for observation

Watch List should mean:
- promising but incomplete
- setup quality is not broken, but still needs confirmation
- resistance, loose structure, or weak volume is still visible

Keep the distinction honest. Promising is not the same as confirmed.

### Step 9 — Keep risk visible and language bounded
End with setup classification and risk framing, not with an instruction to buy.

This skill should surface:
- what looks strong
- what is still missing
- what could invalidate the setup

---

## Failure modes

Avoid:
- skipping hard filters and scoring everything
- using one candle to overrule weak structure
- ignoring volume confirmation
- promoting a Watch-quality setup into Top just because the narrative is attractive
- hiding obvious resistance or breakdown risk
- writing a polished bullish paragraph instead of structured explainability
- using Top List as disguised trade execution language

---

## Tool hints

Usually relevant:
- a market-data loader for OHLCV history
- a config loader for [hard_filter_rules_v1.json](D:/husband-agent-runtime-test/config/hard_filter_rules_v1.json)

Sometimes relevant:
- a future technical-analysis helper for consistent feature engineering

This skill does not execute scoring by itself.

---

## Output expectations

A good output should look close to [sample_top_watch_output.json](D:/husband-agent-runtime-test/samples/sample_top_watch_output.json) and include:

1. `ticker`
2. `sector`
3. `setup_type`
4. candle / volume / location context
5. `trend_quality_score`
6. `volume_confirmation_score`
7. `setup_readiness_score`
8. `final_score`
9. `why_in`
10. `why_not_top`
11. `risk_note`
12. Top List or Watch List classification

The output should stay explainable enough that another layer can inspect why a name was promoted or held back.

---

## Stop conditions

Hold open or abstain when:
- hard filters have not been applied
- OHLCV history is too thin to read structure honestly
- structure is clearly damaged
- the setup is too close to breakdown risk
- volume confirmation is absent and the chart is still too early
- the user wants stronger certainty than the evidence supports

If the setup is promising but incomplete, say:
> watch-quality setup only

---

## One-line summary

> Score candidate stocks by reading candle first, volume second, structure third, then explain exactly why a setup belongs on Top List, Watch List, or nowhere.
