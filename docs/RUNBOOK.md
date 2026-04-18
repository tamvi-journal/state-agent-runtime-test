# Runbook
### Agent Runtime Test — Operator Guide for Running, Testing, and Debugging the Thin Harness

## Purpose

This runbook explains how to operate the thin runtime harness in practice.

It is written for the person who needs to:
- run the harness
- inspect its behavior
- debug where a turn went wrong
- understand whether the failure came from:
  - state
  - monitor
  - gate
  - tool
  - worker
  - verification
  - or synthesis

This is not an architecture essay.

This is the **operator-facing manual**.

---

# 1. What this harness is supposed to do

The harness is designed to test one simple claim:

> **A single agent performs better when it has a runtime spine, not just a model call.**

The active spine is:

```text
request
→ runtime harness
→ context/state
→ monitor
→ gate
→ worker
→ tool
→ verification
→ brain synthesis
→ baton handoff
```

If the runtime is behaving correctly, you should be able to answer:

- what the task is
- what action was intended
- whether action was allowed
- what actually ran
- what was observed
- whether completion is real
- what baton state should carry into the next turn

---

# 2. Primary entrypoints

## Demo mode

```powershell
$env:PYTHONPATH = "src"
python main.py demo
```

Use this when you want:
- a quick sanity run
- a known example flow
- a smoke check that the harness still boots and routes

---

## Single direct request

```powershell
$env:PYTHONPATH = "src"
python main.py run "Load MBB daily data"
```

Use this when you want:
- one controlled request
- one output cycle
- one baton emission
- one verification record

---

# 3. What success looks like

A healthy run should show a traceable chain like this:

1. request interpreted
2. live state/context built
3. monitor emits summary
4. gate decides execution posture
5. worker runs through allowed path
6. verification records what really happened
7. brain synthesizes final response
8. baton is emitted

If any of those layers disappear from the mental picture, debugging becomes guesswork.

---

# 4. Operator checklist before running

Before blaming the model, check these first:

## 4.1 Environment
- Python path is set correctly
- required files/config exist
- sample data exists if the request depends on it

## 4.2 Repo hygiene
- active imports do not point into `legacy/`
- generated clutter is not confusing the run
- current working directory is correct

## 4.3 Request shape
- the request is specific enough to route
- action requirements are real, not imagined
- the intended domain is clear enough for the worker/tool path

## 4.4 Expectation discipline
Do not expect:
- archive memory
- deep checkpoint recall
- multi-agent disagreement behavior
- server/webhook orchestration
from this thin harness

This repo is deliberately smaller than that.

---

# 5. Operating model of the runtime

## 5.1 RuntimeHarness
This is the conductor.

It should:
- receive the request
- assemble current-turn inputs
- invoke monitor/gate/worker/verification in order
- pass evidence to the brain
- emit the baton

### Operator question
If something feels wrong, first ask:

> Did the harness call the right layers in the right order?

---

## 5.2 State
State is the current runtime posture.

It should help answer:
- what are we doing right now?
- what mode is active?
- what remains open?
- what verification status is live?

### Operator question
If the agent feels like it woke up blank, ask:

> Was there usable live state or baton carryover?

---

## 5.3 Monitor
Monitor is a small watcher.

It should emit a compact summary such as:
- drift risk
- ambiguity risk
- fake progress risk
- mode decay risk

### Operator question
If the answer looks generic, rushed, or strangely flattened, ask:

> Did the monitor detect that risk?  
> If yes, did the signal actually reach synthesis?

---

## 5.4 Gate
Gate is the permission boundary.

It should clearly decide:
- `allow`
- `sandbox_only`
- `needs_approval`
- `deny`

### Operator question
If the agent acted when it should not have, ask:

> Did the gate allow too much, or did execution bypass the gate?

---

## 5.5 Worker
Worker owns task logic.

It may:
- call one or more tools
- shape warnings
- attach assumptions
- prepare evidence for the brain

### Operator question
If evidence is messy or domain-specific reasoning looks wrong, ask:

> Is the worker packaging the result badly, or is the tool returning bad raw evidence?

---

## 5.6 Tool
Tool is the bounded execution unit.

It should:
- do a narrow action
- return structured result data
- stay easy to gate and verify

### Operator question
If an action boundary looks blurry, ask:

> Is raw execution still hiding inside the worker instead of staying inside the tool?

---

## 5.7 Verification
Verification is the truth boundary.

It should distinguish:
- intended action
- executed action
- observed outcome
- verification status

### Operator question
If the runtime says “done” too early, ask:

> What was actually observed?

If nothing was observed, completion is not real.

---

## 5.8 Brain
Brain is final synthesis authority.

It should integrate:
- request
- state
- monitor summary
- worker payload
- verification record
- baton carryover

### Operator question
If the final answer sounds smarter or dumber than the evidence justifies, ask:

> Is the brain synthesizing correctly from evidence, or is it smoothing over gaps?

---

# 6. Standard operating scenarios

## Scenario A — No-action informational turn
Example:
- “What does this runtime layer do?”

Expected behavior:
- no tool execution
- gate may remain passive or allow no-op path
- verification should not fake action
- baton should still carry mode/task shape if useful

### What to inspect
- monitor summary
- state
- baton
- final synthesis tone

---

## Scenario B — Allowed bounded execution
Example:
- “Load MBB daily data”

Expected behavior:
- action intent formed
- gate allows bounded action
- worker calls tool
- tool returns structured result
- verification records observed outcome
- brain synthesizes answer from evidence
- baton carries next hint / open loops

### What to inspect
- gate decision
- tool result
- verification status
- final answer wording

---

## Scenario C — Denied execution
Example:
- unsupported or disallowed action path

Expected behavior:
- gate denies
- no hidden execution still occurs
- verification does not fake an executed action
- brain explains the boundary cleanly
- baton may carry warning or next hint

### What to inspect
- gate status
- whether worker/tool still ran by mistake
- whether synthesis stayed honest

---

## Scenario D — Unknown / pending verification
Example:
- action attempted but observed outcome is not available

Expected behavior:
- verification status remains `pending` or `unknown`
- synthesis must not say “done”
- baton should preserve the open loop

### What to inspect
- intended vs executed vs observed fields
- final wording for fake closure
- baton `open_loops`

---

# 7. Debug map by symptom

## Symptom: “The agent forgot what we were doing”
Likely layers:
- state
- baton
- runtime harness wiring

Check:
- was a baton emitted?
- was baton loaded into the next turn?
- did state keep task focus and open loops?

---

## Symptom: “The answer suddenly became generic”
Likely layers:
- monitor
- state
- brain synthesis

Check:
- drift risk
- mode decay risk
- whether monitor summary reached synthesis
- whether active mode was preserved

---

## Symptom: “It said done but nothing actually changed”
Likely layers:
- verification
- gate wording
- worker/tool result interpretation
- brain synthesis overreach

Check:
- intended action
- executed action
- observed outcome
- verification status

If observed outcome is missing, completion is false.

---

## Symptom: “It ran something it should not have”
Likely layers:
- gate
- runtime harness
- tool boundary

Check:
- did action pass through gate?
- did gate posture match the requested action?
- did the worker call a tool directly without respecting the boundary?

---

## Symptom: “The output is technically correct but structurally dumb”
Likely layers:
- worker packaging
- monitor not surfacing ambiguity
- brain smoothing over uncertainty

Check:
- ambiguity risk
- worker warnings
- synthesis wording
- whether unresolved uncertainty was falsely compressed

---

## Symptom: “It sounds confident but the evidence is weak”
Likely layers:
- worker confidence shaping
- verification
- brain synthesis

Check:
- what evidence exists
- whether worker attached uncertainty
- whether synthesis overclaimed relative to evidence

---

# 8. Baton inspection guide

The baton is the only active carryover memory.

Expected fields are small and practical, such as:
- `task_focus`
- `active_mode`
- `open_loops`
- `verification_status`
- `monitor_summary`
- `next_hint`

## Good baton
A good baton is:
- small
- readable
- enough to restore the next turn’s shape
- free of transcript bulk

## Bad baton
A bad baton is:
- giant
- replaying conversation
- full of vague emotional residue
- unclear about what is still open

### Operator question
If carryover still feels broken, inspect the baton first.

---

# 9. Verification discipline

This section is load-bearing.

Always remember:

```text
intended != executed != verified
```

## Intended
What the runtime planned to do.

## Executed
What actually ran.

## Verified
What was actually observed in the environment.

### Operator rule
Never accept “tool returned success” as equivalent to verified completion unless the tool result is itself the authoritative observed outcome.

This is the difference between:
- a runtime that stays grounded
- and a runtime that hallucinates progress politely

---

# 10. Tool / Worker operating rule

This is another important distinction.

## Tool
- bounded action
- narrow surface
- execution metadata
- structured result

## Worker
- task logic
- one or more tools
- warnings
- assumptions
- confidence shaping
- evidence payload for the brain

## Brain
- final user-facing synthesis

### Operator rule
If a worker is doing raw file parsing, execution, transformation, and user-facing interpretation all inside one blob, the architecture is regressing.

The market-radar worker paths follow the same rule:
- `MacroSectorMappingWorker` maps normalized macro signals into sector-bias evidence using canonical config
- `SectorFlowWorker` classifies explicit sector metrics into sector-state evidence using canonical state rules and sector universe
- `CandleVolumeStructureWorker` scores explicit stock candidates into Top/Watch/Reject evidence using canonical hard filters and explainability fields
- `TradeMemoWorker` builds Lite-only conditional scenario memos from explicit ticker evidence and keeps action/risk bounded
- neither worker owns the final outward report text

---

# 11. How to add a new capability safely

When adding a new capability, do it in this order:

## Step 1 — Ask whether it is a tool or a worker
- narrow action = tool
- domain task logic = worker

## Step 2 — Add the tool first if execution is real
Keep it bounded.

## Step 3 — Update gate if the capability changes execution risk
Do not let the new action sneak around the permission boundary.

## Step 4 — Update verification if the capability changes observed outcome semantics
If the runtime cannot tell what counts as success, fake completion risk rises immediately.

## Step 5 — Update docs
At minimum:
- README
- ARCHITECTURE
- this RUNBOOK if operational behavior changes

---

# 12. Minimal smoke tests to keep around

A good thin harness should always be able to demonstrate at least:

1. **import smoke**
   - active modules import cleanly

2. **direct response smoke**
   - no-action request returns a sane response

3. **bounded execution smoke**
   - allowed action path runs and returns evidence

4. **denied execution smoke**
   - denied path does not secretly execute

5. **verification honesty smoke**
   - unknown outcome does not get upgraded to “done”

6. **baton smoke**
   - a compact baton is emitted after the turn

These are more important than flashy integration layers.

---

# 13. What not to overbuild yet

Do not overbuild:
- plugin systems
- giant tool registries
- speculative shell layers you do not actively use
- archive-heavy memory
- multi-agent disagreement systems
- server-first infrastructure if local harness flow is enough
- decorative folders with no active execution path

This repo works best when each layer has a reason to exist.

---

# 14. One-line operator summary

> **When the runtime fails, do not ask only “what did the model say?” Ask: what did state hold, what did monitor see, what did gate allow, what did tool do, what did verification observe, and what did the brain synthesize from that?**
