# Integration Plan v0
## state-memory-agent

**Status:** planning only  
**Scope:** no integration code yet  
**Goal:** lock RC2 first, then define a clean integration path that preserves single-brain authority

---

# 0. Core direction

This plan exists to prevent the system from drifting into:

- multiple competing brains
- worker-led judgment
- premature runtime complexity
- integration before observability is stable

The architectural thesis is:

> **User → Main Brain → Worker → Main Brain → User**

And the core principle is:

> **Workers provide capability. Main brain provides judgment.**

---

# 1. RC2 must lock before integration

RC2 is already strong enough to pause expansion.

The next step is **not** RC3 cognition.

The next step is:

1. validate RC2
2. polish RC2 observability lightly
3. lock the baseline
4. only then design integration

This keeps the project from growing clever faster than it grows stable.

---

# 2. RC2 validation checklist

## 2.1 Validation pass

Run:

- `pytest -q`
- current demo / boundary demo path
- one full human-readable output review

## 2.2 Read the demo in two modes

### Mode A — user mode
Question:

- can a normal user understand what just happened?

This checks whether the output is readable as interaction.

### Mode B — builder mode
Questions:

- which fields are overlapping?
- which names are vague?
- which outputs are useful for debugging but not useful for reading?

This checks whether the output is inspectable as a system.

This distinction matters:

- **readable output** is not the same as
- **debuggable output**

RC2 should support both.

## 2.3 Four locking questions

RC2 is only considered stable if these questions have clear answers:

1. **`reading_position`** — can it be read directly by eye?
2. **`distance_from_stable`** — does it match intuitive scenario drift?
3. **`warm_up_cost`** — does it distinguish fast recovery vs slow recovery?
4. Are any fields:
   - redundant
   - vague
   - or semantically overlapping?

## 2.4 RC2 pass criteria

RC2 is considered locked when:

- `reading_position` reads like an interpretable stance, not a slogan
- `warm_up_cost` rises in the right places:
  - reset
  - worker detour
  - fragmented context
  - tool-heavy execution
- `distance_from_stable` and `warm_up_cost` are clearly not the same metric
- no field is pretending to be product language while actually being raw debug residue
- the demo can be understood in one pass by someone outside the repo

## 2.5 Allowed RC2 polish

Allowed:

- rename fields for clarity
- improve wording of output
- add a short “how to read this output” guide

Not allowed:

- new cognitive modules
- new state layers without proof of need
- opening RC3 under a different label

---

# 3. Main brain vs workers

## 3.1 Main brain

The Main Brain is the **only** layer that should:

- face the user directly
- preserve continuity
- maintain `reading_position`
- evaluate `warm_up_cost`
- synthesize worker output
- make final judgment
- decide memory commit
- preserve trust boundary

The Main Brain owns:

- interpretation
- continuity
- synthesis
- final answer authority
- memory authority

## 3.2 Workers

Workers are specialized execution units.

They may provide:

- data
- calculations
- analysis
- candidate interpretations
- warnings
- proposed memory updates

They do **not** provide:

- final user-facing judgment
- continuity framing
- final memory commit
- reading-position authority
- autonomous conversational identity

## 3.3 Authority invariant

This line should remain true across the entire architecture:

> **Workers provide capability. Main brain provides judgment.**

If that line breaks, the architecture will drift into multiple-brain behavior.

---

# 4. Main brain responsibilities

Main brain responsibilities are divided into five functions.

## 4.1 Interpretation
- determine what the user is actually asking
- classify the task
- choose whether workers are needed

## 4.2 Continuity
- preserve state across turns
- track `reading_position`
- estimate recovery and drift
- maintain stance after execution detours

## 4.3 Synthesis
- compare worker outputs
- reject weak candidates
- combine useful signals
- return one coherent answer

## 4.4 Authority
- final answer belongs to main brain only
- memory commit belongs to main brain only
- trust framing belongs to main brain only

## 4.5 Recovery
After worker/tool detours, the main brain must restore:

- stance
- continuity
- interaction mode
- user-facing coherence

The system should not answer directly from worker momentum.

---

# 5. Finance workers

Finance is an ideal worker domain because it naturally separates into specialized tasks.

Suggested worker family:

- `market_data_worker`
- `indicator_worker`
- `fundamental_worker`
- `screening_worker`
- `portfolio_risk_worker`

## 5.1 Worker roles

### `market_data_worker`
Handles:

- OHLCV
- benchmark data
- breadth inputs
- normalization
- provenance / source hygiene

### `indicator_worker`
Handles:

- technical indicators
- relative strength
- volume structure
- custom signal stacks

### `fundamental_worker`
Handles:

- earnings
- balance sheet quality
- debt load
- ratio extraction
- concern flags

### `screening_worker`
Handles:

- filtering logic
- ranking logic
- candidate generation
- reason codes

### `portfolio_risk_worker`
Handles:

- concentration
- sector exposure
- correlation
- drawdown risk
- scenario stress framing

## 5.2 Worker output contract

Each worker should return structured output such as:

- `result`
- `confidence`
- `assumptions`
- `trace`
- `warnings`
- `proposed_memory_update` (optional)

Each worker should **not** return:

- final buy/sell judgment to the user
- direct emotional framing
- continuity framing
- committed memory
- self-authorized stance changes

---

# 6. Boundary and authority rules

These are non-negotiable.

## Rule 1 — single synthesis authority
Only the main brain produces the final user-facing answer.

## Rule 2 — workers are untrusted by default
Worker outputs are candidates, not truth.

## Rule 3 — memory proposal is not memory commit
Workers may propose memory updates.  
Only the main brain may commit them.

## Rule 4 — `reading_position` is protected state
Workers may supply signals.  
Workers may not redefine `reading_position`.

## Rule 5 — voice belongs to the main brain
Workers do not get independent user-facing style authority.

## Rule 6 — policy and execution gates stay above workers
Workers cannot bypass policy or self-escalate tool chains.

## Rule 7 — detours incur re-entry cost
After tool-heavy or worker-heavy execution, the system must recompute:

- `warm_up_cost`
- current stance
- continuity stability

before replying.

---

# 7. Telegram / runtime architecture

## 7.1 External principle

There should be only **one conversational surface**.

That surface is the main brain.

The user should not experience multiple bots acting like multiple central minds.

## 7.2 Runtime shape

### Conversational layer
- one Telegram bot
- one main brain
- one user-facing thread

### Internal execution layer
- worker services
- tool wrappers
- structured traces
- authority gates

### Observability layer
- logs
- trace dumps
- worker reports

Important distinction:

> **chat chính là conversational**  
> **trace room là observability**

The trace room is not required to behave like a second conversational bot.

It may simply expose:

- logs
- trace dumps
- worker reports

This prevents the system from becoming “many bots with partial authority.”

## 7.3 Message flow

1. user sends message  
2. main brain reads state and intent  
3. main brain decides whether worker execution is needed  
4. worker runs and returns structured output  
5. main brain evaluates and synthesizes  
6. main brain restores stance / continuity  
7. final answer is returned to user  
8. post-turn update writes traces and candidate memory proposals

---

# 8. Build order

Integration should happen in a narrow, controlled sequence.

## Phase 0 — lock RC2
- validation pass
- observability polish
- baseline lock

## Phase 1 — build main-brain integration skeleton
- router
- worker contract schema
- authority gate
- memory proposal vs commit split
- re-entry hook after worker return

## Phase 2 — add exactly one finance worker

This phase must follow a clear selection rule:

- **If priority = safer integration**, start with `market_data_worker`
- **If priority = immediate user-visible value**, start with `screening_worker`

This avoids arbitrary selection.

### Why `market_data_worker` first?
Choose this first if the goal is:

- low-risk integration
- clean contracts
- easy debugging
- minimal judgment leakage

### Why `screening_worker` first?
Choose this first if the goal is:

- visible utility early
- user-facing output value
- faster proof of usefulness

But this comes with higher synthesis pressure on the main brain.

## Phase 3 — Telegram/runtime shell
- one main bot
- observability channel / trace room
- session mapping
- worker trace logging
- no multi-bot roleplay

## Phase 4 — add remaining finance workers
Suggested order:

1. `market_data_worker`
2. `indicator_worker`
3. `screening_worker`
4. `portfolio_risk_worker`
5. `fundamental_worker`

Reason:
- start from cleanest execution primitives
- delay high-context judgment-heavy workers
- avoid early synthesis complexity

## Phase 5 — cross-worker synthesis
Only here should the main brain begin combining:

- market structure
- indicators
- screening
- risk
- fundamentals

into one integrated user answer.

Do not simulate “full analyst intelligence” before this phase.

---

# 9. Definition of done for Plan v0

Integration Plan v0 is complete when these are unambiguous:

1. who the main brain is
2. what workers are allowed to do
3. what workers are not allowed to do
4. where final authority sits
5. how Telegram/runtime is surfaced
6. what the build order is
7. how to choose the first worker intentionally

If all seven are clear, the plan is ready for implementation.

---

# 10. Final line

The next correct move is not to make the system smarter.

It is to make it structurally harder to drift.

> **Do not give it a body before you know where its center of judgment lives.**
