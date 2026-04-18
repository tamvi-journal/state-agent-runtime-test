# Skill: Fundamental Analysis

---
skill_id: fundamental_analysis
title: Fundamental Analysis
domain: finance
use_when:
  - earnings analysis
  - valuation review
  - margin and cash flow interpretation
  - business quality assessment
avoid_when:
  - no financial data is available
  - request is purely chart-based
required_tools:
  - market_data_tool
optional_tools:
  - fundamentals_tool
tags:
  - finance
  - fundamental
  - valuation
  - earnings
---

## Purpose

Use this skill when the task is to analyze a business from its financial performance, quality, and valuation rather than from chart structure alone.

This skill exists to prevent:
- narrative-only investing talk
- cherry-picking one metric
- giving valuation opinions without business context

---

## Use when

Activate this skill when the user asks about:
- revenue
- profit
- margins
- cash flow
- debt
- valuation
- business quality
- earnings trends
- whether a stock is fundamentally strong or weak

---

## Do not use when

Do not use this skill when:
- the request is purely technical/chart based
- no financial statements or relevant data are available
- the user only wants a short-term trade read

---

## Inputs expected

Minimum useful inputs:
- revenue
- profit / net income
- margins
- debt / leverage context
- valuation metrics if available

Useful extras:
- cash flow
- ROE / ROA
- business segment breakdown
- recent filing dates
- multi-period trend data

---

## Method

### Step 1 — Identify the analysis frame
Determine whether the task is:
- quality analysis
- growth analysis
- valuation analysis
- risk analysis
- full quick fundamental pass

Do not mix all frameworks into one vague blob.

---

### Step 2 — Read trend before snapshot
Start with direction over time:
- revenue trend
- earnings trend
- margin trend
- cash flow trend
- debt trend

A single good quarter is not a thesis by itself.

---

### Step 3 — Separate quality from valuation
These are not the same.

Ask:
- is this business improving or deteriorating?
- is this business cheap or expensive?
- is it cheap because it is weak?
- is it expensive because quality deserves it?

Never collapse “good company” into “good buy.”

---

### Step 4 — Check profitability and efficiency
Look at:
- gross margin
- operating margin
- net margin
- return metrics if available

Ask:
- are margins stable, expanding, or compressing?
- are returns supported by real business quality or leverage?

---

### Step 5 — Check balance sheet and survivability
Inspect:
- debt load
- liquidity
- refinancing pressure if visible
- cash conversion
- whether the company has room to survive pressure

A fragile balance sheet changes interpretation of all growth claims.

---

### Step 6 — Check valuation in context
Use valuation only after quality and trend are read.

Examples:
- PE
- PB
- EV multiples
- market cap vs earnings power

Ask:
- cheap relative to what?
- expensive relative to what?
- does the valuation match the quality and growth profile?

---

### Step 7 — Write the actual conclusion
A good conclusion should separate:
- business quality
- financial trend
- risk profile
- valuation posture
- what would change the conclusion

---

## Failure modes

Avoid:
- using PE alone as the whole thesis
- mixing old and new filings without date clarity
- treating one headline metric as enough
- calling a business strong when cash flow is weak and debt is heavy
- confusing “cheap” with “safe”
- ignoring deterioration because the chart looks good

---

## Tool hints

Usually relevant:
- `market_data_tool` for basic symbol context
- a future `fundamentals_tool`

---

## Output expectations

A good output should include:

1. what financial period is being discussed
2. trend summary
3. profitability read
4. balance sheet or survivability note
5. valuation interpretation
6. risk summary
7. final stance with uncertainty clearly bounded

---

## Stop conditions

Hold open or abstain when:
- filing period is unclear
- data freshness is unknown
- key financial lines are missing
- valuation cannot be contextualized
- the user wants certainty stronger than the evidence supports

If evidence is partial, say:
> partial fundamental read only

---

## One-line summary

> Read trend before valuation, separate quality from price, and never confuse a cheap stock with a strong business.
