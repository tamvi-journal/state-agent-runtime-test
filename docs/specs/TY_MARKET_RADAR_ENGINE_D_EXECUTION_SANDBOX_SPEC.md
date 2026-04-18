# TY MARKET RADAR — SPEC ENGINE D
## Execution Sandbox / Paper Trading Bot

## 0. Purpose

Engine D is a **sandboxed execution layer** for testing how the system would behave if it were allowed to trade.

Its primary role is **not live trading**.  
Its primary role is:
- simulate entries and exits
- track hypothetical PnL
- enforce hard risk rules
- journal every trade decision
- measure whether the system's ideas actually work in practice

This engine should begin in:
1. **Shadow mode**
2. **Paper trading mode**
3. only later, if explicitly desired, **micro-live mode**

---

## 1. Position in Whole System

### Engine A — Daily Radar
Finds what is worth looking at:
- macro -> sector -> flow -> ticker
- outputs Top List / Watch List

### Engine B — Quarterly Fundamental Red Flag
Adds anomaly / red-flag context on a separate schedule

### Engine C — Trade Memo / Scenario Planner
Builds scenario-based memo for selected tickers

### Engine D — Execution Sandbox / Paper Trading Bot
Answers:
- if we actually followed the rules, what would happen?
- what would the PnL look like?
- what is the win rate / drawdown / expectancy?
- where do the rules break?

---

## 2. Core Principles

- **Start with paper trading only**
- **No live order routing in V1**
- **LLM cannot freely decide execution**
- **Execution must be rule-gated**
- **Every trade must be logged**
- **Every position must have invalidation**
- **Risk limits override all model enthusiasm**

Ty can later decide whether to upgrade from paper -> micro-live.

---

## 3. Operating Modes

## 3.1 Shadow Mode
The system does not even simulate position management deeply yet.

It only:
- records hypothetical entry signals
- records hypothetical stop / target zones
- tracks what would have happened afterward

Use this mode to validate raw signal quality.

---

## 3.2 Paper Trading Mode
The system behaves like a trader with fake capital.

It can:
- open simulated positions
- close simulated positions
- track realized / unrealized PnL
- track fees / slippage assumptions
- enforce risk rules

This is the default V1 mode.

---

## 3.3 Micro-Live Mode (future only)
Only allowed after:
- paper trading has enough sample size
- risk rules are stable
- Ty explicitly approves real-money routing

Not part of current V1 build.

---

## 4. Engine D Role Split

Engine D should be split into 4 internal components:

### D1 — Signal Intake
Reads valid candidates from Engine A / Engine C.

### D2 — Risk Gate
Decides whether the signal is even allowed to become a trade.

### D3 — Position Simulator
Simulates entry, sizing, partial exits, stop logic, and PnL.

### D4 — Performance Journal
Stores all trades and computes analytics.

---

## 5. Input Sources

Engine D should only consume signals from one of these:

### Input A — Radar-qualified signal
From Engine A:
- ticker
- Top List / Watch List status
- scores
- reasons
- support / resistance
- sector state

### Input B — Trade Memo-confirmed signal
From Engine C:
- scenario table
- action stance
- invalidation zone
- optional DCA ladder

### Input C — Manual override
Ty manually tells the sandbox:
- simulate this ticker
- simulate this ladder
- simulate this capital size

---

## 6. Required Inputs

For each candidate trade:
- `ticker`
- `sector`
- `signal_source` (`radar` / `memo` / `manual`)
- `entry_style` (`market`, `limit_zone`, `breakout_confirm`)
- `entry_zone`
- `invalidation_zone`
- `take_profit_levels`
- `sector_state`
- `trend_quality_score`
- `volume_confirmation_score`
- `setup_readiness_score`
- `final_score`
- `risk_profile`
- `paper_capital`
- `max_risk_per_trade_pct`
- `timestamp`

Optional:
- `dca_plan`
- `time_stop_days`
- `late_entry_risk`
- `macro_conflict_flag`

---

## 7. Risk Rules (Hard Constraints)

These must exist before any trade can be opened.

## 7.1 Global portfolio rules
- max concurrent positions
- max total exposure
- max exposure per sector
- daily loss cap
- weekly loss cap
- pause after losing streak threshold

### Suggested V1 starter defaults
- max concurrent positions: **3**
- max total exposure: **80%**
- max sector exposure: **40%**
- max risk per trade: **1R = 1%–2% of paper capital**
- pause after **3 consecutive losing trades**

---

## 7.2 Position-level rules
- no trade without invalidation zone
- no trade if reward/risk too poor
- no trade if signal is stale
- no trade if setup score is below minimum
- no trade if sector is `WEAKENING`

### Suggested minimums
- final score >= **7.0** for paper entry
- sector state must be `ACTIVE` or `HOT`
- reward/risk >= **1.5**
- signal age <= **1 trading session** unless still valid by rule

---

## 7.3 Anti-overtrade rules
- do not open same ticker twice without reset condition
- do not chase extended HOT sector without explicit allowance
- do not average down unless DCA plan already exists in the original trade design
- do not open more than one new position from the same sector in the same signal burst unless allowed

---

## 8. Execution Logic

## Step 1 — Signal Intake
Receive candidate signal from Engine A or Engine C.

## Step 2 — Eligibility Check
Run the hard constraints:
- score threshold
- sector state allowed?
- invalidation exists?
- signal still fresh?
- capital available?
- sector exposure exceeded?

If any fail:
- reject trade
- log rejection reason

## Step 3 — Position Sizing
Compute simulated size using:
- paper capital
- max risk per trade
- distance from entry to invalidation

Example:
- paper capital: $50
- max risk per trade: 2%
- max loss allowed: $1
- entry 28.5
- stop 27.5
- risk per share = 1.0
- position size = 1 share-equivalent unit

For VN equities, because lot sizes may distort realism, sandbox can support:
- real-lot simulation
- fractional simulation mode for strategy testing

---

## Step 4 — Entry Model

Supported entry styles:

### A. Market-at-next-open
Simplest simulation.

### B. Limit-zone entry
Enter only if price touches the zone.

### C. Breakout-confirm entry
Enter only if breakout condition and volume condition are met.

Recommended V1:
- support **limit-zone** and **breakout-confirm**
- keep market-next-open only for simple testing

---

## Step 5 — Position State Machine

Each position should have a state:
- `PENDING`
- `OPEN`
- `PARTIAL_EXIT`
- `CLOSED_WIN`
- `CLOSED_LOSS`
- `CANCELLED`
- `EXPIRED`

### Example lifecycle
1. signal created
2. pending order exists
3. entry triggered -> open
4. TP1 hit -> partial exit
5. stop moved or remains fixed
6. final exit -> closed

---

## 9. Exit Rules

Engine D should support:

### 9.1 Hard stop
Exit if invalidation zone is breached.

### 9.2 Partial take-profit
Optional staged exits:
- TP1
- TP2
- TP3

### 9.3 Time stop
Exit if trade goes nowhere after X days.

### 9.4 Structural failure exit
Exit if:
- sector state flips to WEAKENING
- breakout fully fails
- price closes below critical support

### 9.5 Memo-driven exit
If Engine C provided explicit scenario invalidation, Engine D may inherit it as a rule.

---

## 10. Required Output Structure

## 10.1 Trade signal intake JSON
```json
{
  "workflow_name": "execution_sandbox_engine",
  "run_id": "2026-03-29-exec-001",
  "timestamp": "2026-03-29T02:30:00Z",
  "status": "success",
  "data": {
    "paper_capital": 50,
    "risk_profile": "balanced",
    "candidate_trades": [
      {
        "ticker": "PVD",
        "sector": "oil_gas",
        "signal_source": "memo",
        "entry_style": "breakout_confirm",
        "entry_zone": "29.2-29.4",
        "invalidation_zone": "below 27.0",
        "take_profit_levels": ["30.5-31.0", "31.8-32.2", "32.5+"],
        "sector_state": "ACTIVE",
        "final_score": 8.4,
        "risk_reward_estimate": 1.8
      }
    ]
  }
}
```

---

## 10.2 Trade journal row
```json
{
  "trade_id": "PVD-2026-03-29-001",
  "ticker": "PVD",
  "entry_date": "2026-03-29",
  "entry_price": 29.3,
  "position_size": 1,
  "capital_allocated": 29.3,
  "invalidation_price": 27.0,
  "tp1_price": 30.8,
  "tp2_price": 32.0,
  "exit_price": null,
  "status": "OPEN",
  "realized_pnl": 0,
  "unrealized_pnl": 0.4,
  "reason_opened": ["sector_active", "breakout_confirmed"],
  "reason_closed": []
}
```

---

## 10.3 Performance summary JSON
```json
{
  "workflow_name": "execution_sandbox_engine",
  "run_id": "2026-04-30-exec-summary-001",
  "timestamp": "2026-04-30T12:00:00Z",
  "status": "success",
  "data": {
    "paper_capital_start": 50,
    "paper_capital_current": 53.4,
    "net_return_pct": 6.8,
    "trade_count": 14,
    "win_rate_pct": 50,
    "avg_win_r_multiple": 1.9,
    "avg_loss_r_multiple": -1.0,
    "expectancy_r": 0.45,
    "max_drawdown_pct": 4.2,
    "open_positions": 1,
    "closed_positions": 13
  }
}
```

---

## 11. Storage Requirements

Engine D needs its own history store.

### Required tables / sheets

#### `paper_trade_signals`
- datetime
- ticker
- signal_source
- entry_style
- entry_zone
- invalidation_zone
- allowed_to_trade
- rejection_reason

#### `paper_positions`
- trade_id
- ticker
- status
- entry_date
- entry_price
- size
- capital_allocated
- stop_price
- tp1
- tp2
- tp3
- exit_date
- exit_price
- realized_pnl
- unrealized_pnl

#### `paper_trade_events`
- datetime
- trade_id
- event_type
- event_note

#### `paper_performance_history`
- date
- paper_capital
- open_risk
- net_return_pct
- max_drawdown_pct
- trade_count

---

## 12. Metrics to Track

Engine D should compute at least:
- total trades
- win rate
- loss rate
- average win
- average loss
- expectancy
- profit factor
- max drawdown
- average hold time
- best sector
- worst sector
- most common failure reason
- most common rejection reason

This is where the sandbox becomes useful.

---

## 13. Reporting Modes

## 13.1 Trade-open notice
Example:
```text
PAPER TRADE OPENED
Ticker: PVD
Entry: 29.3
Stop: 27.0
TP1: 30.8
Reason: breakout confirmed + sector ACTIVE
Capital used: $29.3
```

## 13.2 Trade-close notice
Example:
```text
PAPER TRADE CLOSED
Ticker: PVD
Exit: 30.8
PnL: +1.5
Reason: TP1 hit and full close rule triggered
```

## 13.3 Weekly sandbox report
Example:
```text
PAPER TRADING SUMMARY
Start capital: $50
Current capital: $53.4
Net return: +6.8%
Trade count: 14
Win rate: 50%
Max drawdown: 4.2%
```

---

## 14. Safety / Guardrails

Engine D must never:
- place real orders in V1
- bypass the hard risk gate
- open a position without stop logic
- inflate probabilities to justify execution
- add new trades just because current positions are losing
- revenge trade after losses

### Important separation
- Engine A finds
- Engine C explains
- Engine D tests execution discipline

Do not let Engine D rewrite the thesis on its own.

---

## 15. Recommended Build Priority

### Phase D1 — Shadow trading
Build first:
- signal logging
- hypothetical outcome tracking
- no real position state machine yet

### Phase D2 — Paper trading core
Then add:
- open/close simulated positions
- risk gate
- journal
- PnL summary

### Phase D3 — Advanced paper features
Later:
- partial exits
- DCA simulation
- time stops
- sector exposure rules
- weekly performance review

### Phase D4 — Micro-live (future only)
Only if Ty explicitly requests.

---

## 16. Suggested Workflow Name

Canonical V1 name:
`execution_sandbox_engine`

Possible internal subflows:
- `execution_signal_gate`
- `paper_position_manager`
- `paper_trade_journal`
- `paper_performance_report`

---

## 17. Example V1 Flow

1. Engine A produces Top List
2. Engine C produces memo for selected tickers
3. Engine D receives only valid candidates
4. Risk gate checks:
   - score high enough?
   - sector OK?
   - stop defined?
   - capital available?
5. If yes:
   - simulate entry
   - open paper position
   - start journaling
6. Track exit conditions daily
7. Compute summary

---

## 18. One-Line Summary

Engine D is a **rule-gated paper trading sandbox** that tests how the radar and memo layers would perform under actual execution discipline, without risking real money in V1.
