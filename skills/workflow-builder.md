# Skill: Workflow Builder

---
skill_id: workflow_builder
title: Workflow Builder
domain: builder
use_when:
  - workflow design
  - n8n-style automation
  - step-by-step agent pipeline design
  - orchestration planning
avoid_when:
  - the task is pure coding with no workflow layer
  - no trigger/action structure is needed
required_tools: []
optional_tools:
  - workflow_tool
  - n8n_tool
tags:
  - workflow
  - automation
  - orchestration
  - n8n
---

## Purpose

Use this skill when the task is to design or revise a workflow rather than write isolated code.

This skill exists to prevent:
- node spaghetti
- unclear trigger/action boundaries
- missing verification checkpoints
- workflows that look complete but are operationally fragile

---

## Use when

Activate this skill when the user asks for:
- a workflow
- automation pipeline
- n8n flow
- step-by-step orchestration
- agent execution pipeline
- decision path / branching logic

---

## Do not use when

Do not use this skill when:
- the task is just one script
- there is no trigger / input / output flow
- the user only wants a plain explanation, not a workflow

---

## Inputs expected

Useful inputs:
- trigger source
- input type
- desired output
- external systems involved
- approval requirements
- verification requirements
- failure tolerance

---

## Method

### Step 1 — Define trigger and terminal state
Ask:
- what starts the workflow?
- what counts as finished?
- what counts as failed?
- what remains pending if verification is incomplete?

Without these, the workflow is fake-clean.

---

### Step 2 — Identify the minimum stages
Usually:
1. trigger
2. input normalization
3. decision / routing
4. action execution
5. verification
6. output / notification
7. handoff or persistence if needed

Do not start with 20 nodes.

---

### Step 3 — Separate logic from action
A workflow should clearly separate:
- interpret/route
- do
- verify

This is the same law as the runtime harness:
> intent != execution != verified outcome

---

### Step 4 — Add failure and retry posture
For each risky step, ask:
- what can fail?
- should it retry?
- should it stop?
- should it notify?
- should it remain open?

A workflow without failure posture is not finished.

---

### Step 5 — Mark approval boundaries
If a step changes something meaningful, ask:
- should this be auto-run?
- sandbox only?
- approval required?
- denied unless explicit override?

---

### Step 6 — Keep the graph readable
A good workflow should be explainable in one sentence per stage.
If not, it is probably too tangled.

---

## Failure modes

Avoid:
- branching before defining terminal state
- mixing data cleanup, action, and verification in one stage
- assuming webhook success = business success
- adding clever loops before basic clarity exists
- overusing subflows when one clear flow is enough

---

## Tool hints

Usually relevant:
- a future `workflow_tool`
- a future `n8n_tool`

---

## Output expectations

A good output should include:
- trigger
- main stages
- action boundaries
- verification stage
- failure handling
- approval points
- concise description of data flow

---

## Stop conditions

Hold open when:
- trigger is unclear
- output definition is vague
- external system boundaries are unknown
- approval requirement is unspecified but matters
- verification criteria are missing

---

## One-line summary

> Design the flow around trigger, action, and verification first; everything decorative comes later.
