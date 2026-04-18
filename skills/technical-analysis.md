# Skill: Technical Analysis

---
skill_id: technical_analysis
title: Technical Analysis
domain: finance
use_when:
  - chart analysis
  - trend structure
  - RSI/KDJ/MACD interpretation
  - volume analysis
  - support/resistance review
avoid_when:
  - no price/volume data is available
  - the request is purely fundamental
required_tools:
  - market_data_tool
optional_tools:
  - technical_analysis_tool
tags:
  - finance
  - ta
  - chart
  - structure
---

## Purpose

Use this skill when the task is to analyze market structure from price and volume rather than from financial statements.

This skill is designed to prevent a common failure:
- jumping straight to indicators
- overclaiming from one signal
- giving a confident directional opinion without first reading structure

---

## Use when

Activate this skill when the user asks for:
- technical analysis
- trend reading
- chart structure
- support/resistance
- momentum confirmation
- indicator interpretation
- entry / risk framing based on chart data

---

## Do not use when

Do not use this skill when:
- no OHLCV data is available
- the request is mainly about earnings, valuation, cash flow, or balance sheet
- the task is purely macro / narrative without chart data

---

## Inputs expected

Minimum useful inputs:
- OHLCV data
- timeframe being analyzed
- ticker / market symbol
- optional benchmark / sector context

Useful extras:
- multi-timeframe data
- recent range highs/lows
- moving averages
- volume averages
- relative strength context

---

## Method

### Step 1 — Establish timeframe and context
Ask or identify:
- what timeframe matters here?
- short-term trade, swing, or position context?
- does the user want structure only, or a directional leaning too?

If timeframe is unclear, state the assumption.

---

### Step 2 — Read structure before indicators
Inspect first:
- trend direction
- higher highs / higher lows vs lower highs / lower lows
- compression / expansion
- range behavior
- breakout vs rejection
- support / resistance zones

Do **not** begin with RSI/MACD/KDJ.
Indicators are secondary.

---

### Step 3 — Check volume behavior
Volume should answer:
- is the move supported?
- is breakout volume real or weak?
- is decline happening on heavy or light volume?
- is there accumulation / distribution behavior?

If price move and volume disagree, lower confidence.

---

### Step 4 — Add indicator overlays
Use indicators only after structure is read.

Suggested order:
1. momentum indicators
2. moving averages
3. confirmation / divergence

Examples:
- RSI for momentum and overextension
- KDJ for faster turning pressure
- MACD for trend/momentum confirmation
- MA structure for trend health

Do not let one indicator override structure.

---

### Step 5 — Compare price, volume, and indicator alignment
Classify the setup:

- **Aligned bullish**
- **Aligned bearish**
- **Mixed / conflicted**
- **Range / unresolved**
- **Breakout attempt without confirmation**
- **Weak move / likely fake strength**

If signals conflict, say so directly.

---

### Step 6 — Frame risk, not prophecy
A good technical read should define:
- current structure
- what confirms the bullish/bearish case
- what invalidates it
- what remains unresolved

Do not talk like the market owes the setup a result.

---

## Failure modes

Avoid these mistakes:
- indicator-first reading
- calling a top or bottom from one candle
- ignoring volume
- treating a breakout candle as a confirmed breakout without follow-through
- mixing timeframes carelessly
- sounding certain when structure is still range-bound
- giving “buy now” language without clear invalidation logic

---

## Tool hints

Usually relevant:
- `market_data_tool`

Sometimes relevant:
- a future `technical_analysis_tool`
- benchmark / sector comparison tools

---

## Output expectations

A good output should contain:

1. timeframe assumption
2. structure read
3. volume read
4. indicator confirmation or conflict
5. current leaning
6. invalidation condition
7. confidence level or uncertainty note

Recommended phrasing style:
- structure first
- conclusion second
- invalidation included
- avoid emotional language

---

## Stop conditions

Hold open or abstain when:
- market data is missing
- timeframe is unclear and matters materially
- only one weak signal is present
- price structure is unresolved
- data quality is questionable
- the request asks for certainty stronger than the evidence allows

If evidence is mixed, say:
> tentative read only

---

## One-line summary

> Read structure first, volume second, indicators third, and never let a neat indicator story outrun the chart itself.
