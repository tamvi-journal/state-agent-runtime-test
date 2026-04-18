# Worker Contract Examples
## state-memory-agent

**Status:** draft  
**Purpose:** provide concrete worker output examples that match the operating model  
**Scope:** first two worker types only — `market_data_worker` and `screening_worker`

---

# 0. Why this file exists

The repo already defines the rule:

> **Workers provide capability. Main brain provides judgment.**

That rule is correct but still abstract until concrete worker payloads exist.

This file gives implementation-facing examples so the first worker integrations do not drift into:
- raw tool dumping
- silent authority creep
- inconsistent output shapes
- worker-led user interpretation

---

# 1. Global contract rule

Every worker output should be shaped like this:

```json
{
  "worker_name": "",
  "result": {},
  "confidence": 0.0,
  "assumptions": [],
  "warnings": [],
  "trace": [],
  "proposed_memory_update": null
}
```

## Required meaning of each field

### `worker_name`
Identifies which capability produced the payload.

### `result`
Structured output only.  
No final user-facing prose authority.

### `confidence`
Worker’s local confidence in its own output quality.  
This is not final truth confidence for the whole system.

### `assumptions`
Explicit conditions the worker relied on.

### `warnings`
Known weaknesses, gaps, or caveats.

### `trace`
Short execution trail for debugging and observability.

### `proposed_memory_update`
Optional suggestion only.  
Never a commit.

---

# 2. Example A — market_data_worker

## 2.1 Purpose

`market_data_worker` should be the safest first worker if priority is integration stability.

It should:
- fetch
- normalize
- validate
- report provenance

It should **not**:
- recommend buy/sell
- narrate market meaning as final judgment
- decide portfolio action

## 2.2 Example output

```json
{
  "worker_name": "market_data_worker",
  "result": {
    "ticker": "MBB",
    "timeframe": "1D",
    "bars_found": 120,
    "date_range": {
      "start": "2025-10-01",
      "end": "2026-04-10"
    },
    "latest_bar": {
      "date": "2026-04-10",
      "open": 24.8,
      "high": 25.2,
      "low": 24.6,
      "close": 25.1,
      "volume": 18450200
    },
    "benchmark_used": "VNINDEX",
    "data_source": "normalized_local_cache",
    "integrity_checks": {
      "missing_dates_detected": false,
      "duplicate_rows_detected": false,
      "volume_null_detected": false,
      "price_order_valid": true
    }
  },
  "confidence": 0.96,
  "assumptions": [
    "daily OHLCV data is already normalized",
    "benchmark mapping for ticker is valid",
    "latest local cache reflects intended dataset"
  ],
  "warnings": [
    "worker did not interpret trend significance",
    "worker did not evaluate indicator context",
    "worker did not verify upstream exchange corrections beyond local snapshot"
  ],
  "trace": [
    "received request for ticker=MBB timeframe=1D",
    "loaded normalized local cache",
    "validated OHLCV field integrity",
    "returned latest bar and metadata"
  ],
  "proposed_memory_update": null
}
```

## 2.3 Why this shape is good

This shape is good because:

- it is clearly **data-first**
- provenance is visible
- integrity checks are explicit
- the worker does not pretend to be analyst-in-chief
- main brain can later interpret without losing boundary clarity

## 2.4 What bad output looks like

Bad output example:

```json
{
  "worker_name": "market_data_worker",
  "result": "MBB looks strong and could continue rising. Good chance to buy."
}
```

Why this is bad:
- raw interpretation hides assumptions
- no provenance
- no integrity checks
- worker starts acting like final strategist

---

# 3. Example B — screening_worker

## 3.1 Purpose

`screening_worker` is useful when priority is user-visible value earlier.

It should:
- apply explicit filters
- rank candidates
- expose reason codes
- show filter pass/fail logic

It should **not**:
- make final portfolio judgment
- hide the selection criteria
- pretend ranked output is final conviction

## 3.2 Example output

```json
{
  "worker_name": "screening_worker",
  "result": {
    "screen_name": "rs_volume_structure_v1",
    "universe_size": 312,
    "passed_count": 4,
    "filters_applied": [
      "close_above_sma50",
      "rs_63d_above_threshold",
      "avg_volume_20d_above_minimum",
      "no_integrity_flags"
    ],
    "candidates": [
      {
        "ticker": "MBB",
        "rank": 1,
        "reason_codes": [
          "close_above_sma50",
          "rs_63d_strong",
          "volume_support_present"
        ],
        "metrics": {
          "close": 25.1,
          "sma50": 23.9,
          "rs_63d": 87.4,
          "avg_volume_20d": 15200400
        }
      },
      {
        "ticker": "VCI",
        "rank": 2,
        "reason_codes": [
          "close_above_sma50",
          "rs_63d_strong",
          "volume_support_present"
        ],
        "metrics": {
          "close": 41.3,
          "sma50": 38.7,
          "rs_63d": 84.1,
          "avg_volume_20d": 9642100
        }
      }
    ]
  },
  "confidence": 0.82,
  "assumptions": [
    "input universe was pre-cleaned",
    "indicator calculations were generated from latest available local dataset",
    "screen thresholds match current strategy version"
  ],
  "warnings": [
    "ranking is mechanical and not a final judgment",
    "screen does not include event risk or news risk",
    "screen does not replace portfolio concentration analysis"
  ],
  "trace": [
    "loaded screening universe",
    "applied filter stack rs_volume_structure_v1",
    "ranked passed candidates by weighted score",
    "returned top candidates with reason codes"
  ],
  "proposed_memory_update": {
    "summary": "Current preferred screen configuration: rs_volume_structure_v1",
    "priority": "low"
  }
}
```

## 3.3 Why this shape is good

This shape is good because:

- the filter logic is inspectable
- reason codes are explicit
- ranking is presented as **mechanical output**
- warnings make clear that screening is not full judgment
- main brain can combine this with risk, structure, and broader context later

## 3.4 What bad output looks like

Bad output example:

```json
{
  "worker_name": "screening_worker",
  "result": {
    "best_pick": "MBB"
  },
  "confidence": 0.97
}
```

Why this is bad:
- hides criteria
- confidence becomes misleading
- worker starts behaving like a final recommender
- no assumptions / warnings / trace / inspectability

---

# 4. Example of main-brain handling

## 4.1 Good synthesis pattern

The main brain should transform worker payloads into final reasoning such as:

- market_data_worker confirms data integrity and latest price context
- screening_worker identifies mechanically strong candidates
- final user-facing judgment remains pending until broader synthesis is complete

This preserves the rule:

> worker output is evidence  
> main-brain output is judgment

## 4.2 Bad synthesis pattern

Bad pattern:
- worker ranking is copied directly into user answer
- confidence score is treated as whole-system conviction
- warnings are dropped
- assumptions disappear

This creates authority leakage.

---

# 5. Recommended validation checks

Before accepting any new worker contract, verify:

- [ ] output matches schema
- [ ] result is structured, not raw persuasive prose
- [ ] assumptions are visible
- [ ] warnings are visible
- [ ] trace is present
- [ ] memory proposal is optional and non-authoritative
- [ ] worker does not sound like final judge
- [ ] main brain still has meaningful synthesis work to do

---

# 6. Selection guidance

## If priority is safer first integration
Start with:
- `market_data_worker`

Why:
- lower semantic authority pressure
- easier to validate
- lower risk of judgment leakage

## If priority is earlier visible user value
Start with:
- `screening_worker`

Why:
- candidates appear immediately useful
- user sees output value quickly

Tradeoff:
- higher risk that worker output is mistaken for final judgment

---

# 7. Closing line

The first worker contract should feel slightly underpowered, not impressive.

That is a feature.

A worker that looks modest but keeps authority clean is better than a worker that sounds brilliant and quietly steals the center.
