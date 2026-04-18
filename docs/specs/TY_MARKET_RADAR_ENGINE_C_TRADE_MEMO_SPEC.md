# TY MARKET RADAR — SPEC ENGINE C
## Trade Memo / Scenario Planner

## 0. Purpose

Engine C is a **deep-dive layer** that sits **after** the Daily Radar system.

It does **not** scan the whole market.
It takes a **small shortlist of tickers** already surfaced by the radar (Top List / Watch List) or selected manually by Ty, then generates a structured **trade memo / scenario plan** for each ticker.

Its role is:
- turn radar output into a readable decision memo
- structure bullish / neutral / bearish scenarios
- define triggers, targets, risk notes, and timeline
- optionally generate a position plan / DCA ladder
- support Ty's judgment without replacing it

---

## 1. Position in Whole System

### Engine A — Daily Radar
Finds what is worth looking at:
- macro -> sector -> flow -> ticker
- outputs Top List / Watch List

### Engine B — Quarterly Fundamental Red Flag
Checks financial anomalies on a separate schedule

### Engine C — Trade Memo / Scenario Planner
Takes 1–5 selected tickers and answers:
- what is the setup?
- what are the scenarios?
- what would a plan look like?
- what invalidates the thesis?

---

## 2. Core Principles

- **No auto-buy / sell**
- **No order execution**
- **No pretending certainty**
- Output must stay **scenario-based**, **trigger-based**, and **conditional**
- Memo must separate:
  - current setup
  - possible paths
  - risk / invalidation
  - optional action plan

Ty still decides whether money goes in.

---

## 3. Input Modes

## Mode A — Radar-fed
Input comes from Engine A:
- ticker is in Top List or Watch List
- sector state already known
- technical scores already known

## Mode B — Manual ticker select
Ty gives:
- 1 or more tickers
- optional style preference
- optional risk profile
- optional capital size

---

## 4. Use Cases

Engine C should be used when:
- Ty wants to zoom in on 1–3 names from Top List
- Ty wants a clean scenario table
- Ty wants a structured plan instead of raw chart notes
- Ty wants a readable memo to review later
- Ty wants lite daily memo or full deep-dive memo

It should **not** be used for:
- every stock in the universe
- every Watch List name every day
- automatic action without review

---

## 5. Output Modes

## 5.1 Lite Memo
Short, daily-usable format.

### Includes:
- setup summary
- 3-scenario table
- action today
- risk note

### Good for:
- Telegram
- fast review
- daily workflow

---

## 5.2 Full Memo
Longer, more detailed format.

### Includes:
- setup summary
- scenario table
- timeline
- trigger map
- optional DCA ladder
- optional TP / SL structure
- invalidation conditions
- optional catalyst notes

### Good for:
- deeper review
- 1–3 favorite names
- weekend planning
- exporting to docs

---

## 6. Required Inputs

## 6.1 Required technical/context inputs
For each ticker:
- `ticker`
- `sector`
- `sector_state`
- `current_price`
- `trend_quality_score`
- `volume_confirmation_score`
- `setup_readiness_score`
- `final_score`
- `setup_type`
- `why_in`
- `why_not_top`
- `risk_note`
- `support_zone`
- `resistance_zone`
- `ma20`
- `ma50`
- `ma200`
- `rsi`
- `macd_state`
- optional `kdj_state`
- recent range / structure note
- catalyst note if any

## 6.2 Optional user inputs
- `memo_mode`: `lite` / `full`
- `risk_profile`: `conservative` / `balanced` / `aggressive`
- `capital_reference`: e.g. 50M, 100M, 500M
- `holding_style`: `swing` / `position`
- `time_horizon`: e.g. 2-6 weeks, 3-12 months

---

## 7. Workflow Logic

## Step 1 — Intake
Receive selected tickers and their latest radar-derived data.

## Step 2 — Normalize state
Build a compact context object for each ticker:
- technical state
- sector state
- catalyst context
- major risk note
- score profile

## Step 3 — Setup Summary
Write a short summary:
- why this ticker deserves attention
- what is currently good
- what is currently missing
- whether the setup is early / active / extended / risky

## Step 4 — Scenario Engine
For each ticker, build 3 scenarios:
- **Bullish**
- **Neutral**
- **Bearish**

Each scenario must include:
- probability estimate
- target zone
- timeline
- trigger conditions

## Step 5 — Action Layer
Depending on mode:
- Lite mode: simple action today
- Full mode: optional entry ladder / DCA / take-profit structure / invalidation level

## Step 6 — Render output
Return structured JSON + human-readable memo text.

---

## 8. Scenario Rules

Engine C must **not** hallucinate arbitrary certainty.

Scenarios must be conditioned on:
- technical triggers
- support/resistance structure
- sector state continuation or deterioration
- catalyst presence/absence
- score strength

### Example triggers
- reclaim MA20 / MA50
- hold support zone
- breakout above resistance
- MACD cross up
- RSI reset / RSI recovery
- volume expansion confirmation
- sector state moving WATCH -> ACTIVE / ACTIVE -> HOT
- sector weakening or broad market deterioration

---

## 9. Required Output Structure

## 9.1 JSON output schema
```json
{
  "workflow_name": "trade_memo_engine",
  "run_id": "2026-03-29-memo-001",
  "timestamp": "2026-03-29T02:00:00Z",
  "status": "success",
  "data": {
    "memo_mode": "lite",
    "ticker_memos": [
      {
        "ticker": "PVD",
        "sector": "oil_gas",
        "setup_summary": {
          "status": "active_setup",
          "good_points": [
            "sector_active",
            "volume_confirmed",
            "strong_close"
          ],
          "missing_points": [
            "still_near_short_term_resistance"
          ],
          "main_risk": "follow-through failure under resistance"
        },
        "scenario_table": [
          {
            "scenario": "bullish",
            "probability_pct": 55,
            "target_zone": "31.0-32.5",
            "timeline": "2-6 weeks",
            "triggers": [
              "hold above breakout zone",
              "volume stays above average",
              "sector remains ACTIVE or HOT"
            ]
          },
          {
            "scenario": "neutral",
            "probability_pct": 25,
            "target_zone": "28.5-30.0",
            "timeline": "2-4 weeks",
            "triggers": [
              "sideways consolidation",
              "volume cools down",
              "market lacks catalyst"
            ]
          },
          {
            "scenario": "bearish",
            "probability_pct": 20,
            "target_zone": "26.5-27.5",
            "timeline": "1-3 weeks",
            "triggers": [
              "lose support zone",
              "sector weakens",
              "breakout fails"
            ]
          }
        ],
        "action_today": {
          "stance": "watch_or_partial_entry",
          "reason": "setup is promising but still close to resistance",
          "next_best_signal": "clean breakout with volume"
        },
        "risk_plan": {
          "invalidation_zone": "below 27.0",
          "risk_note": [
            "near resistance",
            "depends on sector continuation"
          ]
        }
      }
    ]
  }
}
```

---

## 10. Human-Readable Output Format

## 10.1 Lite Memo format
For each ticker:

### 1. Setup Summary
- why this name is interesting
- what is good now
- what is still missing

### 2. Scenario Table
| Scenario | Prob | Target | Timeline | Trigger |
|---|---:|---|---|---|

### 3. Action Today
- wait
- partial entry
- watch only
- avoid for now

### 4. Risk Note
- invalidation
- main structural risk

---

## 10.2 Full Memo format
For each ticker:
1. Setup Summary
2. Scenario Table
3. Timeline / catalyst notes
4. Optional DCA ladder
5. Optional TP / SL logic
6. Invalidation conditions
7. Final note: “what would make me more confident?”

---

## 11. Optional Position Plan Layer

This layer is optional and should only appear when:
- `memo_mode = full`
- `capital_reference` is given
- Ty explicitly wants ladder guidance

### Allowed outputs
- DCA ladder
- staged allocation
- simple TP ladder
- invalidation zone

### Not allowed
- certainty language like “must buy now”
- auto order size suggestions detached from scenario logic
- leverage suggestions by default

### Example DCA structure
```json
{
  "position_plan": {
    "capital_reference": "500M VND",
    "allocation_style": "staged_entry",
    "levels": [
      {
        "label": "1st buy",
        "price_zone": "28.0-28.3",
        "capital_pct": 40,
        "purpose": "core position"
      },
      {
        "label": "2nd buy",
        "price_zone": "27.3-27.7",
        "capital_pct": 30,
        "purpose": "add on dip"
      },
      {
        "label": "3rd buy",
        "price_zone": "breakout retest only",
        "capital_pct": 20,
        "purpose": "confirmation add"
      }
    ],
    "cash_reserve_pct": 10
  }
}
```

---

## 12. Risk / Safety Rules

Engine C must:
- keep probabilities rough, not fake precision
- keep action conditional
- always state invalidation
- always carry forward at least 1 risk note
- prefer “if X then Y” over “this will happen”

### Forbidden output styles
- prophecy tone
- guaranteed target language
- urging immediate action without trigger conditions
- pretending to know future catalysts with certainty

---

## 13. Trigger Templates

### Bullish triggers
- reclaim MA20 / MA50
- breakout with volume
- sector state improves
- MACD crosses up
- RSI recovers from reset
- clean retest holds

### Neutral triggers
- range holds
- low-vol consolidation
- sector remains mixed
- no strong catalyst

### Bearish triggers
- support fails
- breakdown with volume
- sector state weakens
- market breadth deteriorates
- failed breakout

---

## 14. Integration With Other Engines

## From Engine A -> Engine C
Engine A should pass:
- ticker shortlist
- sector state
- technical scores
- reasons / risks
- key chart zones

## From Engine C -> Ty
Engine C returns:
- readable memo
- scenario table
- structured risk/action note

## Engine C does not feed Engine A back automatically
Keep it one-way at V1:
- Radar finds
- Memo explains

---

## 15. Suggested Workflow Name

### Recommended
`trade_memo_engine`

### Alternatives
- `scenario_planning_engine`
- `ticker_deep_dive_engine`
- `position_plan_engine`

Use `trade_memo_engine` as canonical V1 name.

---

## 16. Build Priority

### Phase C1 — Lite Memo
Build first:
- setup summary
- scenario table
- action today
- risk note

### Phase C2 — Full Memo
Build later:
- position plan
- DCA ladder
- TP logic
- catalyst timeline

This keeps V1 lighter and more stable.

---

## 17. Sample Plain-Text Lite Memo

```text
TRADE MEMO — PVD

1. Setup Summary
- Sector: Oil & Gas (ACTIVE)
- Why it is interesting: sector is active, volume confirmed, close quality strong
- What is missing: still near short-term resistance
- Main risk: breakout could fail without follow-through

2. Scenario Table
- Bullish (55%): 31.0-32.5 in 2-6 weeks if breakout holds and volume stays strong
- Neutral (25%): 28.5-30.0 in 2-4 weeks if price consolidates under resistance
- Bearish (20%): 26.5-27.5 in 1-3 weeks if support fails and sector weakens

3. Action Today
- Stance: watch or partial entry
- Better signal: clean breakout with volume

4. Risk Note
- Invalidation: below 27.0
- Key risk: near resistance, depends on sector continuation
```

---

## 18. One-Line Summary

Engine C is a **post-radar deep-dive layer** that turns shortlisted tickers into **scenario-based, trigger-based trade memos** so Ty can think more clearly without handing over final decision authority.
