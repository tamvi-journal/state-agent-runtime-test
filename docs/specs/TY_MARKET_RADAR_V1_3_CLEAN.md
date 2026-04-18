# TY MARKET RADAR — IMPLEMENTATION SPEC V1.3-CLEAN

## 0. Purpose

Build an automated **Vietnam stock market radar** using **n8n**.

The system should:
- scan international macro/news signals each morning
- map those signals into Vietnam sector implications
- confirm or reject those implications with real VN market flow
- filter candidate stocks
- score candle / volume / structure quality
- split outputs into **Top List** and **Watch List**
- send morning reports, state-change alerts, and weekly reviews

### Core principles
- **No automatic buy/sell decisions**
- **No order placement**
- **Daily technical/flow radar is separate from quarterly financial analysis**
- **Ty makes final trading decisions**

---

## 1. System Architecture

The system has **2 main engines**.

### Engine A — Daily Technical / Flow Radar
Used for:
- morning report
- intraday / end-of-day alert
- weekly review

### Engine B — Quarterly Fundamental Red Flag Engine
Used for:
- quarterly financial-report screening
- red flags / positive flags / need-review labels

---

## 2. Parent Workflow

## `ty_market_hq`

### Role
- orchestrate child workflows
- normalize outputs
- build final reports
- send output to Telegram / Google Sheet / Excel / optional email

### Child workflows
1. `morning_macro_scan`
2. `macro_to_vn_sector_map`
3. `sector_flow_check`
4. `stock_candidate_filter`
5. `candle_volume_structure_engine`
6. `report_builder`
7. `alert_engine`
8. `weekly_review_engine`

Quarterly engine runs separately:
9. `quarterly_financial_redflag_engine`

---

## 3. Phase 0 — Prerequisites

**Phase 0 must be completed before Phase 1 starts.**

### Checklist
- [ ] Lock VN market data primary source
- [ ] Lock VN market data fallback source
- [ ] Test 30 days OHLCV fetch successfully
- [ ] Prepare sector / industry mapping file
- [ ] Build initial `macro_sector_map.json`
- [ ] Set up n8n on server
- [ ] Set up Telegram bot + target chat/group
- [ ] Set up storage for state history
- [ ] Confirm global RSS/news feeds work inside n8n

### Recommended source strategy

#### Global news
- **Primary:** Reuters RSS
- **Fallback:** one additional structured global feed

#### VN market data
Choose **1 primary** and **1 fallback**.

Candidates:
- Fireant API
- SSI Fast Connect / iBoard-related feed
- VNDirect
- TCBS API
- other stable structured OHLCV source

#### Quarterly financial data
Use separate source later, for example:
- VietstockFinance
- CafeF
- other parseable financial-report source

### Recommended V1 decision
- **Primary market data:** Fireant API or SSI Fast Connect
- **Fallback market data:** VNDirect or TCBS API
- **Macro-sector map:** local JSON maintained by Ty

---

## 4. Storage Strategy

The system must store history from day 1.

### V1 recommendation
Start with **Google Sheet** for ease of debugging and manual inspection.

### V2 migration option
Move to **SQLite** when alert/state comparison gets heavier.

### Minimum history tables / sheets

#### `sector_state_history`
Fields:
- date
- sector
- state
- rs_score
- volume_regime
- breadth_score
- change_from_previous

#### `stock_top_watch_history`
Fields:
- date
- ticker
- sector
- list_type (`TOP` / `WATCH` / `REMOVED`)
- final_score
- why_in
- why_not_top
- risk_note

#### `alert_history`
Fields:
- datetime
- alert_type
- sector
- ticker
- message
- was_sent

#### `macro_signal_history`
Fields:
- date
- theme
- direction
- strength_score
- matched_trigger
- decay_remaining

---

## 5. Macro-to-Sector Map — Core Brain

This is the most important judgment layer of the whole system.

## Required file
- `macro_sector_map.json`

Without this file, the system is only an aggregator, not a radar.

### Each trigger must define
- positive VN sectors
- negative VN sectors
- watch tickers
- confidence
- decay period
- notes

### Required fields
- `trigger_key`
- `vn_sectors_positive`
- `vn_sectors_negative`
- `watch_stocks`
- `confidence`
- `decay_days`
- `notes`

### Example
```json
{
  "oil_up": {
    "trigger_key": "oil_up",
    "vn_sectors_positive": ["oil_gas", "fertilizer"],
    "vn_sectors_negative": ["airlines", "transport"],
    "watch_stocks": {
      "oil_gas": ["PVD", "PVS", "BSR"],
      "fertilizer": ["DPM", "DCM", "LAS"],
      "airlines": ["HVN", "VJC"]
    },
    "confidence": "medium",
    "decay_days": 3,
    "notes": "Higher oil prices may support upstream/refining and pressure fuel-sensitive sectors."
  }
}
```

### Required starter triggers
- `hormuz_risk`
- `oil_up`
- `oil_down`
- `china_stimulus`
- `usd_strength`
- `fed_dovish`
- `fed_hawkish`
- `commodity_up`
- `commodity_down`
- `global_risk_on`
- `global_risk_off`

### Recommended additional triggers
- `vnd_depreciation`
- `china_property_crisis`
- `gold_up`
- `rate_cut_vn`
- `election_cycle`
- `fdi_inflow`
- `export_demand_shift`

### Guidance for `decay_days`
- short shock events: **1–3 days**
- medium macro events: **5–10 days**
- longer policy effects: **15–30 days**

### Important rule
Ty maintains this map manually.  
AI may suggest expansions, but the judgment layer must be validated by Ty.

---

## 6. Workflow Specifications

## 6.1 `morning_macro_scan`

### Purpose
Scan global news and produce **5–10 meaningful macro signals**.

### Inputs
- RSS / API / international feeds
- tracked topic list:
  - oil
  - rates
  - USD
  - Fed
  - China
  - war / geopolitical conflict
  - tariff / trade
  - commodities
  - global risk sentiment

### Process
1. fetch 20–50 recent headlines
2. deduplicate
3. classify by theme
4. score importance
5. normalize direction / sentiment
6. reduce to 5–10 usable signals

### Implementation note
- Steps 1–2 can be code-only
- Steps 3–6 can use LLM with structured JSON output

### Output
```json
{
  "scan_date": "YYYY-MM-DD",
  "global_signals": [
    {
      "signal_id": "oil_001",
      "theme": "oil",
      "headline": "Brent rises on Middle East tension",
      "summary": "Oil extended gains after renewed geopolitical tension.",
      "direction": "positive",
      "strength_score": 8.4,
      "confidence": "high",
      "time_horizon": "short_term",
      "source": "Reuters"
    }
  ]
}
```

---

## 6.2 `macro_to_vn_sector_map`

### Purpose
Translate global signals into Vietnam sector implications.

### Inputs
- `global_signals`
- `macro_sector_map.json`

### Process
1. read each signal
2. match signal to trigger map
3. produce sector bias output
4. attach confidence and decay
5. attach watch tickers

### Output
```json
{
  "vn_sector_bias": [
    {
      "trigger_signal_id": "oil_001",
      "sector": "oil_gas",
      "direction": "positive",
      "strength_score": 8.1,
      "confidence": "medium",
      "decay_days": 3,
      "reason": "oil_up"
    },
    {
      "trigger_signal_id": "oil_001",
      "sector": "airlines",
      "direction": "negative",
      "strength_score": 6.8,
      "confidence": "medium",
      "decay_days": 3,
      "reason": "fuel_cost_pressure"
    }
  ]
}
```

---

## 6.3 `sector_flow_check`

### Purpose
Verify whether real VN market flow confirms the macro story.

### Inputs
- sector universe
- sector or representative-basket OHLCV
- benchmark VNIndex
- `vn_sector_bias`

### Required metrics
- sector % change
- sector volume vs MA20
- breadth score
- up/down ratio
- breakout count
- breakdown count
- sector RS vs VNIndex

### Sector states
- `WATCH`
- `ACTIVE`
- `HOT`
- `WEAKENING`

### Initial rule logic

#### WATCH
- macro or narrative bias exists
- RS starts improving
- breadth not yet strong
- volume not fully confirmed

#### ACTIVE
- RS above threshold
- breadth strong
- volume above MA20
- at least one or more leaders confirm

#### HOT
- ACTIVE conditions still hold
- breakout count expands
- multiple leaders confirm
- strong breadth persists

#### WEAKENING
- RS deteriorates
- breadth worsens
- volume confirmation fades
- breakdown count rises

### Output
```json
{
  "sector_flow_board": [
    {
      "sector": "oil_gas",
      "state": "ACTIVE",
      "direction": "positive",
      "rs_score": 82,
      "volume_regime": "expanded",
      "breadth_score": 8.0,
      "up_down_ratio": 3.4,
      "breakout_count": 4,
      "breakdown_count": 0,
      "macro_alignment": true
    }
  ]
}
```

---

## 6.4 `stock_candidate_filter`

### Purpose
Filter candidate stocks from sectors worth attention.

### Inputs
- `sector_flow_board`
- stock universe
- stock OHLCV
- benchmark data

### Hard filters
- minimum liquidity threshold
- RS above threshold
- exclude clearly illiquid names
- exclude structurally broken names
- exclude names near obvious breakdown zones
- include only sectors in `WATCH`, `ACTIVE`, or `HOT`

### Output
```json
{
  "stock_candidates": [
    {
      "ticker": "PVD",
      "sector": "oil_gas",
      "sector_state": "ACTIVE",
      "liquidity_score": 8.4,
      "rs_score": 81,
      "price_structure_ok": true,
      "candidate_reason": [
        "sector_active",
        "liquidity_ok",
        "rs_strong",
        "structure_intact"
      ]
    }
  ]
}
```

---

## 6.5 `candle_volume_structure_engine`

### Purpose
Read OHLCV structure and classify candidates into **Top List** or **Watch List**.

### Inputs
- OHLCV 60–150 sessions
- candidate stock list
- optional indicators:
  - MA20 / MA50 / MA200
  - RSI
  - KDJ
  - RS
  - volume MA20

### Structure
This workflow should be split into **2 internal layers**.

### Layer 1 — Feature engineering

#### Candle features
- body size
- upper wick
- lower wick
- close position
- range expansion / contraction
- momentum candle
- indecision / doji / reversal bar

#### Volume features
- volume vs MA20
- volume vs recent 3–5 sessions
- expansion / contraction
- volume-range alignment

#### Structure features
- location: bottom / base / top
- near resistance / near support
- above or below MA20 / MA50 / MA200
- base tightness vs looseness
- breakout / retest / failed breakout
- recent sequence across 3–10 bars

#### Relative features
- RS improving / weakening
- sector strong / weak
- leader / laggard inside sector

### Layer 2 — Scoring and classification

#### Required scores
- `trend_quality_score`
- `volume_confirmation_score`
- `setup_readiness_score`

#### Required explainability
- `why_in`
- `why_not_top`
- `risk_note`

### Initial classification logic

#### Top List
- sector is `ACTIVE` or `HOT`
- RS supportive
- structure high quality
- candle/volume confirmation present
- setup readiness high

#### Watch List
- promising but incomplete
- sector only starting to improve
- structure incomplete
- missing volume confirmation
- near resistance
- requires 1–2 more confirming sessions

### Initial calibration guidance
Do **not** hard-freeze thresholds before observing real output.

Suggested starting point:
- **Top List:** all 3 scores >= 7.5, or average >= 7.5 with no score below 6.0
- **Watch List:** average 5.5–7.4
- **Reject:** average below 5.5 or any score below 4.0

### Suggested rollout
- Weeks 1–2: run scoring broadly, let Ty review outputs
- Weeks 3+: adjust thresholds based on real-market fit

### Output
```json
{
  "top_list": [
    {
      "ticker": "PVD",
      "sector": "oil_gas",
      "setup_type": "base_breakout",
      "scores": {
        "trend_quality_score": 8.5,
        "volume_confirmation_score": 8.0,
        "setup_readiness_score": 8.7,
        "final_score": 8.4
      },
      "why_in": ["strong_close", "volume_expansion", "sector_active"],
      "why_not_top": [],
      "risk_note": ["near_short_term_resistance"]
    }
  ],
  "watch_list": [
    {
      "ticker": "DPM",
      "sector": "fertilizer",
      "setup_type": "base_forming",
      "scores": {
        "trend_quality_score": 7.2,
        "volume_confirmation_score": 5.8,
        "setup_readiness_score": 6.4,
        "final_score": 6.5
      },
      "why_in": ["base_ok", "sector_watch"],
      "why_not_top": ["needs_volume_confirmation"],
      "risk_note": ["still_under_resistance"]
    }
  ]
}
```

---

## 6.6 `report_builder`

### Purpose
Convert structured output into readable report text.

### Morning report sections
1. Global pulse
2. VN sector impact
3. Sector flow board
4. Top List
5. Watch List

### Rules
- concise
- reason-based
- readable on Telegram
- no absolute buy/sell language

### Output example
```text
TY MARKET RADAR — Morning

1. Global pulse
- Oil up on Middle East tension
- USD firm after Fed remarks

2. VN sector impact
- Oil & Gas: Positive
- Fertilizer: Watch positive
- Airlines: Negative

3. Sector flow
- Oil & Gas: ACTIVE
- Fertilizer: WATCH
- Securities: WEAKENING

4. Top List
- PVD
- PVS
- BSR

5. Watch List
- DPM
- DCM
- LAS
```

---

## 6.7 `alert_engine`

### Purpose
Send alerts when state changes matter.

### Trigger conditions
- sector moves `WATCH -> ACTIVE`
- sector moves `ACTIVE -> HOT`
- sector moves `ACTIVE/HOT -> WEAKENING`
- stock moves from Watch List to Top List
- breakout confirmation
- retest confirmation
- breakdown / structure loss

### Anti-spam rules
- cooldown by ticker
- cooldown by sector
- only re-alert on true state change
- batch alerts by sector when multiple names fire together

### Failure rule
No silent failure. If alert workflow fails, system should notify Ty.

### Output example
```text
ALERT — Sector Change
Oil & Gas moved from WATCH to ACTIVE.
Leading names: PVD, PVS, BSR.
Reason: sector breadth strong + volume expansion + RS improvement.
```

---

## 6.8 `weekly_review_engine`

### Purpose
Summarize the week.

### Inputs
- weekly OHLCV and RS
- sector state history
- top/watch history
- alert history

### Output
- top sectors of the week
- emerging sectors
- weakening sectors
- stocks holding structure
- stocks losing momentum

### Output example
```text
WEEKLY REVIEW

Top sectors:
- Oil & Gas
- Fertilizer

Emerging:
- Securities

Weakening:
- Banking

Stocks holding structure:
- PVD, DPM, SSI

Stocks losing momentum:
- AAA, BBB
```

---

## 7. Quarterly Engine

## `quarterly_financial_redflag_engine`

### Schedule
Run in:
- January
- April
- July
- October

### Purpose
Separate quarterly anomaly screening.

### Labels
- `POSITIVE_FLAG`
- `RED_FLAG`
- `NEED_REVIEW`

### Required checks
- revenue QoQ / YoY
- profit QoQ / YoY
- gross margin
- operating cash flow
- inventory
- receivables
- debt
- EPS
- profit up but CFO negative
- inventory spike
- receivables spike
- unusual margin deterioration

### Important rule
Quarterly engine does **not** directly override the daily ranking.
It is an extra risk/quality layer for Ty to inspect.

### Output
```json
{
  "financial_flags": [
    {
      "ticker": "ABC",
      "flag_type": "RED_FLAG",
      "issues": [
        "receivables_spike",
        "cfo_negative_while_profit_up"
      ]
    }
  ]
}
```

---

## 8. Output Channels

Priority channels:
- Telegram
- Google Sheet
- Excel export
- optional weekly email

---

## 9. Failure Modes and Safety Rules

### Failure modes to handle
- news feed down
- market API schema changes
- unmatched macro triggers
- too many sectors active at once
- workflow/server failures

### Required handling
- fallback source where possible
- validate incoming schema before processing
- log unmatched signals for manual review
- cap Top List output size
- send workflow-failure notice instead of failing silently

### Anti-patterns the system must avoid
- chasing sectors already too extended without flagging late-entry risk
- forcing macro and flow to match when they conflict
- silently dropping failed runs

---

## 10. Phase Build Order

## Phase 1
- `morning_macro_scan`
- `macro_to_vn_sector_map`
- `sector_flow_check`
- `report_builder`

## Phase 2A
- `stock_candidate_filter`

## Phase 2B
- `candle_volume_structure_engine`

## Phase 3
- `alert_engine`

## Phase 4
- `weekly_review_engine`

## Phase 5
- `quarterly_financial_redflag_engine`

---

## 11. Role Split

- **Ty** = direction, VN market judgment, final decision-making
- **Lam / GPT** = architecture, decomposition, spec logic
- **Claude Code / implementation tool** = coding and file generation

---

## 12. One-Line System Summary

**Global news -> VN sector mapping -> real flow confirmation -> stock filtering -> candle/volume/structure scoring -> Top List / Watch List -> report to Ty**,  
with **quarterly financial red-flag screening kept separate**.
