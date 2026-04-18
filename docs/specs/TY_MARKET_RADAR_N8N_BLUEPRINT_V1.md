# TY MARKET RADAR — N8N IMPLEMENTATION PLAN / BLUEPRINT V1

## 0. Goal

Turn the current spec into a **buildable n8n system** with:
- a daily market radar
- sector-state tracking
- candidate stock filtering
- Top List / Watch List output
- alerting
- weekly review
- a separate quarterly red-flag engine

This blueprint is written so Claude Code / co-work / dev can start implementation with minimal guessing.

---

## 1. Build philosophy

### What this system is
A **workflow-first market radar**.

### What this system is not
- not a trading executor
- not an auto-order bot
- not a chatbot-first product
- not a full quant engine

### Priority order
1. data reliability
2. workflow stability
3. readable outputs
4. scoring sophistication
5. surface polish

---

## 2. Recommended project structure

```text
ty_market_radar/
├─ config/
│  ├─ macro_sector_map_v1.json
│  ├─ sector_universe_v1.json
│  ├─ hard_filter_rules_v1.json
│  └─ sector_state_rules_v1.json
├─ samples/
│  ├─ sample_morning_macro_scan.json
│  ├─ sample_macro_to_vn_sector_map.json
│  ├─ sample_sector_flow_output.json
│  ├─ sample_stock_candidates.json
│  ├─ sample_top_watch_output.json
│  ├─ sample_report_output.json
│  ├─ sample_alert_output.json
│  └─ sample_weekly_review_output.json
├─ workflows/
│  ├─ ty_market_hq.json
│  ├─ morning_macro_scan.json
│  ├─ macro_to_vn_sector_map.json
│  ├─ sector_flow_check.json
│  ├─ stock_candidate_filter.json
│  ├─ candle_volume_structure_engine.json
│  ├─ report_builder.json
│  ├─ alert_engine.json
│  ├─ weekly_review_engine.json
│  └─ quarterly_financial_redflag_engine.json
├─ docs/
│  ├─ TY_MARKET_RADAR_V1_3_CLEAN.md
│  ├─ TY_MARKET_RADAR_JSON_SCHEMAS.md
│  └─ TY_MARKET_RADAR_N8N_BLUEPRINT_V1.md
└─ runtime/
   ├─ exports/
   ├─ logs/
   └─ cache/
```

---

## 3. System topology

## Parent workflow
### `ty_market_hq`
Role:
- orchestrates the child workflows
- manages timing
- collects output
- routes to Telegram / Sheet / Excel

### Child workflows
1. `morning_macro_scan`
2. `macro_to_vn_sector_map`
3. `sector_flow_check`
4. `stock_candidate_filter`
5. `candle_volume_structure_engine`
6. `report_builder`
7. `alert_engine`
8. `weekly_review_engine`

Separate:
9. `quarterly_financial_redflag_engine`

---

## 4. Phase 0 — setup tasks before any workflow

## 4.1 Lock data sources
Choose:
- **global news primary**
- **global news fallback**
- **VN data primary**
- **VN data fallback**

### Suggested starter choice
- global news primary: Reuters RSS
- global news fallback: secondary structured feed
- VN primary: Fireant API or SSI Fast Connect
- VN fallback: VNDirect or TCBS API

## 4.2 Confirm config files
Must exist before Phase 1:
- `macro_sector_map_v1.json`
- `sector_universe_v1.json`
- `hard_filter_rules_v1.json`
- `sector_state_rules_v1.json`

## 4.3 Storage
Start with:
- Google Sheet for state history

Required tabs:
- `sector_state_history`
- `stock_top_watch_history`
- `alert_history`
- `macro_signal_history`

## 4.4 Telegram
Need:
- bot token
- destination chat/group id
- test message success

## 4.5 Server / n8n
Need:
- n8n running
- credentials configured
- environment variables stored
- workflow export/import path ready

---

## 5. Environment variables

Recommended env keys:

```env
NEWS_RSS_PRIMARY=https://...
NEWS_RSS_FALLBACK=https://...
VN_DATA_API_PRIMARY=https://...
VN_DATA_API_FALLBACK=https://...
VN_DATA_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
GOOGLE_SHEET_ID=...
TZ=Asia/Ho_Chi_Minh
```

Optional:
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.4-mini
LLM_API_KEY=...
```

---

## 6. Scheduling plan

## 6.1 Morning radar
Run:
- every trading day
- suggested time: **07:00–07:30 ICT**

Purpose:
- macro scan
- sector map
- early sector bias
- first morning report

## 6.2 Market-close / late-session check
Run:
- every trading day
- suggested time: **14:45–15:10 ICT**

Purpose:
- confirm real flow
- update sector states
- build Top / Watch
- send alert/report refresh if needed

## 6.3 Weekly review
Run:
- once per week
- suggested time: **Saturday morning**

## 6.4 Quarterly red-flag engine
Run:
- January
- April
- July
- October
- plus optional manual rerun

---

## 7. Parent workflow blueprint — `ty_market_hq`

## Trigger node
- **Cron**
- one instance for morning run
- one instance for close/late-session run
- one instance for weekly run
- quarterly workflow separate

## Node sequence (conceptual)
1. `Set Run Metadata`
2. `Load Config Files`
3. `Branch by run_type`
4. If `morning`:
   - call `morning_macro_scan`
   - call `macro_to_vn_sector_map`
   - call `sector_flow_check`
   - optional early `report_builder`
5. If `close`:
   - call `sector_flow_check`
   - call `stock_candidate_filter`
   - call `candle_volume_structure_engine`
   - call `report_builder`
   - call `alert_engine`
   - append history
6. If `weekly`:
   - call `weekly_review_engine`
7. Send output
8. Failure branch -> send failure notice

## Recommended n8n nodes
- Cron
- Set
- Read Binary File / local file read
- HTTP Request
- Code
- If
- Execute Workflow
- Google Sheets
- Telegram
- Merge
- Switch

---

## 8. Child workflow blueprint details

## 8.1 `morning_macro_scan`

### Nodes
1. `Trigger from parent`
2. `Fetch primary RSS`
3. `Fetch fallback RSS` (only if primary fails or returns too little)
4. `Normalize headlines`
5. `Deduplicate`
6. `Optional LLM classify/summarize`
7. `Build global_signals JSON`
8. `Write macro_signal_history`
9. `Return payload`

### Implementation note
#### Without LLM
Can still work in v0:
- keyword-based theme detection
- simple scoring rules
- weaker quality

#### With LLM
Better:
- theme classification
- importance scoring
- compact summaries
- JSON-only output enforced

### Minimal fallback mode
If LLM fails:
- still return raw normalized signals
- mark `status = warning`

---

## 8.2 `macro_to_vn_sector_map`

### Nodes
1. `Input from parent`
2. `Load macro_sector_map_v1.json`
3. `Code node: match signals to triggers`
4. `Apply decay_days`
5. `Attach watch_stocks`
6. `Return vn_sector_bias`

### Key logic
- one signal can map to multiple sectors
- multiple signals can hit same sector
- keep all matched triggers
- merge confidence conservatively

### Recommended merge approach
For same sector:
- keep strongest directionally aligned trigger
- add list of supporting trigger ids
- do not over-inflate confidence blindly

---

## 8.3 `sector_flow_check`

### Purpose
Turn sector data into sector states.

### Data requirement
Need either:
- sector indices / baskets
or
- representative ticker basket by sector

### Nodes
1. `Input vn_sector_bias`
2. `Load sector_universe_v1.json`
3. `Fetch OHLCV / breadth data`
4. `Code node: compute sector metrics`
5. `Code node: apply sector_state_rules_v1.json`
6. `Compare with previous state history`
7. `Write sector_state_history`
8. `Return sector_flow_board`

### Must-compute metrics
- sector change %
- volume ratio vs MA20
- breadth score
- up/down ratio
- breakout count
- breakdown count
- RS score
- leader count
- macro_alignment

### Important rule
If macro says positive but flow is negative:
- keep both
- mark conflict
- do not force alignment

---

## 8.4 `stock_candidate_filter`

### Nodes
1. `Input sector_flow_board`
2. `Load hard_filter_rules_v1.json`
3. `Fetch stock-level OHLCV for enabled sectors`
4. `Code node: compute pre-filter metrics`
5. `Apply hard filters`
6. `Return stock_candidates`

### Output target
Small, cleaner list only.
Do not send everything into candle engine.

### Good V1 behavior
If too many candidates:
- cap by sector
- prioritize sectors in `HOT`, then `ACTIVE`, then `WATCH`

Suggested cap:
- 3–5 stocks per sector at this stage

---

## 8.5 `candle_volume_structure_engine`

Split internally into **2 blocks**.

### Block A — feature engineering
Nodes:
1. `Input candidates`
2. `Fetch detailed OHLCV history`
3. `Code node: candle features`
4. `Code node: volume features`
5. `Code node: structure features`
6. `Code node: relative features`

### Block B — scoring and classification
Nodes:
7. `Code node: compute three core scores`
8. `Code node: final_score`
9. `Code node: why_in / why_not_top / risk_note`
10. `Split into top_list / watch_list / reject`

### V1 simplification
Do not overbuild pattern recognition.
Start with:
- strong close
- momentum candle
- quiet base candle
- drying volume
- expanded volume
- above/below MA20/50
- near support/resistance
- simple breakout/retest logic

Add advanced logic later.

---

## 8.6 `report_builder`

### Nodes
1. `Input from sector/candidate/score workflows`
2. `Assemble sections`
3. `Code node: render plain text`
4. `Optional: render HTML/Markdown`
5. `Return report`

### Output variants
- morning report
- close update
- weekly review

### V1 priority
Telegram plain text first.

---

## 8.7 `alert_engine`

### Nodes
1. `Input current sector_flow_board + current top/watch`
2. `Read previous sector states and top/watch history`
3. `Detect true changes`
4. `Apply cooldown rules`
5. `Group alerts by sector if needed`
6. `Write alert_history`
7. `Send Telegram alert`
8. `Return alert payload`

### Must-have protections
- no duplicate alerts within cooldown
- no re-send without state change
- no spam if many names fire at once

Suggested cooldown:
- sector alerts: 4–6 hours
- ticker alerts: 1 trading session

---

## 8.8 `weekly_review_engine`

### Nodes
1. `Read last 5 trading days history`
2. `Aggregate sector performance`
3. `Aggregate state transitions`
4. `Aggregate top/watch movements`
5. `Render weekly review`
6. `Send Telegram / email`
7. `Return report`

### Weekly review should answer
- who led
- who emerged
- who weakened
- who held structure
- who lost momentum

---

## 8.9 `quarterly_financial_redflag_engine`

This workflow should stay independent.

### Nodes
1. `Quarterly cron trigger`
2. `Fetch financial data`
3. `Normalize issuer rows`
4. `Code node: red-flag checks`
5. `Code node: positive-flag checks`
6. `Label: POSITIVE_FLAG / RED_FLAG / NEED_REVIEW`
7. `Write output sheet`
8. `Optional summary message`

### V1 priority
Use it as a screening layer only.
No direct effect on daily ranking.

---

## 9. Google Sheet design for V1

## Sheet 1 — `sector_state_history`
Columns:
- date
- run_id
- sector
- state
- rs_score
- volume_regime
- breadth_score
- up_down_ratio
- breakout_count
- breakdown_count
- macro_alignment
- flags

## Sheet 2 — `stock_top_watch_history`
Columns:
- date
- run_id
- ticker
- sector
- list_type
- final_score
- trend_quality_score
- volume_confirmation_score
- setup_readiness_score
- why_in
- why_not_top
- risk_note

## Sheet 3 — `alert_history`
Columns:
- datetime
- run_id
- alert_type
- sector
- ticker
- message
- cooldown_until
- was_sent

## Sheet 4 — `macro_signal_history`
Columns:
- date
- run_id
- signal_id
- theme
- headline
- direction
- strength_score
- confidence
- matched_trigger
- decay_remaining

---

## 10. Build order — real implementation sequence

## Step 1
Import config files and make sure n8n can read them.

## Step 2
Build `morning_macro_scan`

## Step 3
Build `macro_to_vn_sector_map`

## Step 4
Build `sector_flow_check`

## Step 5
Build minimal `report_builder`
- enough to send morning macro/sector output

## Step 6
Build `stock_candidate_filter`

## Step 7
Build `candle_volume_structure_engine`
- first simple version only

## Step 8
Build `alert_engine`

## Step 9
Build `weekly_review_engine`

## Step 10
Build `quarterly_financial_redflag_engine`

---

## 11. Recommended milestone releases

## Milestone M1 — “Radar breathes”
Working:
- morning macro scan
- sector mapping
- sector flow
- simple report

## Milestone M2 — “Radar points”
Working:
- stock candidate filter
- Top / Watch output

## Milestone M3 — “Radar warns”
Working:
- alerts
- state change detection
- cooldown

## Milestone M4 — “Radar remembers”
Working:
- weekly review
- history becomes useful

## Milestone M5 — “Radar cross-checks”
Working:
- quarterly financial red-flag engine

---

## 12. Failure-handling blueprint

Every workflow should have:
- success path
- warning path
- failure path

### Failure path behavior
If a critical workflow fails:
- send Telegram notice
- write a log row
- do not fail silently

### Suggested failure message
```text
TY MARKET RADAR — WORKFLOW FAILURE
Workflow: sector_flow_check
Run: 2026-03-29-morning-001
Reason: VN data source schema mismatch
Action: fallback source needed
```

---

## 13. V1 anti-overengineering rules

For V1:
- prefer plain JSON over clever abstractions
- prefer readable Code nodes over compressed magic
- prefer one clear rule over five fuzzy ones
- prefer stable reports over pretty reports
- prefer fewer alerts over noisy alerts

---

## 14. Hand-off instructions for Claude Code / dev

### What to build first
1. file loading layer
2. morning macro scan
3. macro-sector map application
4. sector flow state engine
5. Telegram output

### What to postpone
- advanced pattern libraries
- heavy ML scoring
- complex dashboard UI
- database migration
- order execution

### Expected dev output
- n8n workflow JSON files
- helper scripts if needed
- config reader logic
- testable mock run path using sample JSON

---

## 15. One-line blueprint summary

Build **a workflow-first VN market radar** that goes:

**global signals -> VN sector implications -> real flow confirmation -> stock filtering -> setup scoring -> Top/Watch output -> Telegram delivery**,  
with **history tracking and quarterly anomaly screening kept separate and modular**.
