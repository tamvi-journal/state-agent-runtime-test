# Skills System Spec
### Agent Runtime Test — Procedural Knowledge Layer for a Thin Single-Agent Harness

## Purpose

This document defines a **skills system** for the thin agent runtime harness.

The runtime already has:
- brain
- state
- monitor
- gate
- tools
- workers
- verification
- baton handoff

What it does **not** yet formalize is:

> **how the agent should carry reusable procedural knowledge without hardcoding everything into the brain or burying it inside workers.**

That is what the skills layer is for.

A skill is not an action.
A skill is not a tool.
A skill is not raw memory.
A skill is not a prompt dump.

A skill is:

> **a reusable procedural knowledge unit that tells the agent how to approach a recurring class of task.**

---

# 1. Core distinction

This repo should keep the following layers cleanly separate.

## Brain
The final synthesis authority.

Question it answers:
> What should the agent say or conclude now?

---

## Tool
A bounded execution unit.

Question it answers:
> What narrow action can the runtime perform safely?

Examples:
- read a file
- fetch market data
- run bounded shell
- call HTTP
- parse CSV

---

## Worker
A task performer that may call one or more tools.

Question it answers:
> How should this specific task be executed and shaped into evidence?

Examples:
- market data worker
- workflow builder worker
- app builder worker
- technical analysis worker

---

## Skill
A procedural knowledge unit.

Question it answers:
> What method, playbook, checklist, or workflow should guide the agent for this class of task?

Examples:
- how to analyze technical structure
- how to build an n8n workflow
- how to scaffold a small web app
- how to do fundamental stock analysis
- how to write strong creative prompts

---

## Baton
A compact carryover object.

Question it answers:
> What minimum structure should the next turn inherit?

---

# 2. Why skills should exist

Without skills, procedural knowledge tends to leak into the wrong places.

It gets buried inside:
- giant prompts
- worker implementation blobs
- ad hoc brain heuristics
- old archived docs
- implicit operator expectations

That creates several failures:

## Failure A — Brain bloat
The brain starts carrying too much domain procedure inline.

## Failure B — Worker opacity
Workers become giant undocumented task blobs.

## Failure C — Prompt spaghetti
Procedural know-how gets duplicated across prompts and is hard to maintain.

## Failure D — Inconsistent behavior
The agent solves the same class of problem differently every time because the method is not formalized anywhere.

## Failure E — Hard-to-debug domain drift
When output quality drops, nobody knows whether the problem came from:
- reasoning
- tool execution
- missing procedure
- or inconsistent task method

The skills system exists to make procedural knowledge:
- explicit
- reusable
- inspectable
- loadable on demand
- separate from execution

---

# 3. What a skill is

A skill is a document-like unit that describes how to perform or reason through a recurring task class.

A skill may contain:
- problem framing
- method steps
- checklists
- common failure modes
- decision rules
- output style rules
- required tool hints
- stop conditions
- escalation rules

A skill should **not** contain:
- raw execution authority
- direct environment mutation
- secret config
- long transcript history
- domain clutter unrelated to the skill’s purpose

---

# 4. Skills vs memory

This distinction matters.

## Memory
Memory is about:
- continuity
- carryover
- anchors
- open loops
- prior state

Memory answers:
> What should persist from previous turns?

---

## Skill
Skill is about:
- method
- procedure
- domain know-how
- reusable playbook logic

Skill answers:
> How should this kind of task be approached?

### Practical difference
- Memory says: “we were analyzing MBB and verification is still open.”
- Skill says: “when doing technical analysis, inspect structure before indicator overlays, and do not overclaim from one timeframe.”

So skills are **not** memory.
They are closer to:
> **procedural knowledge modules**

---

# 5. Skills vs tools

This distinction is also load-bearing.

## Tool
- acts
- bounded
- executable
- gateable
- verifiable

## Skill
- guides
- procedural
- text or structured knowledge
- not executable by itself
- helps the brain/worker choose good method

### Example
For technical analysis:

- `market_data_tool.py` → loads price/volume data
- `technical_analysis_worker.py` → computes and packages evidence
- `technical_analysis.md` skill → tells the agent how to interpret the analysis in a disciplined order

That is the right split.

---

# 6. System role of skills

The skills system should function as:

> **an on-demand procedural knowledge layer that can be loaded into the runtime when a task class requires a reusable method.**

It should sit conceptually between:
- raw reasoning
- and raw execution

Skills shape the method.
Tools shape the action.
Workers shape the task result.
Brain shapes the final synthesis.

---

# 7. Where skills should live

Recommended active path:

```text
skills/
  technical-analysis.md
  fundamental-analysis.md
  coin-analysis.md
  workflow-builder.md
  app-builder.md
  creative-prompting.md
```

Optional future subfolders if the library grows:

```text
skills/
  finance/
    technical-analysis.md
    fundamental-analysis.md
    coin-analysis.md
  builder/
    workflow-builder.md
    app-builder.md
    repo-refactor.md
  creative/
    creative-prompting.md
    image-prompting.md
    music-prompting.md
```

For the thin harness, start flat unless there is enough real content to justify grouping.

---

# 8. Skill object model

A skill should be readable both:
- by humans
- by the runtime

Recommended minimal skill structure:

```md
# Skill: Technical Analysis

## Purpose
What this skill is for.

## Use when
When the runtime should activate this skill.

## Do not use when
Where the skill does not apply.

## Inputs expected
What the worker/brain should already have.

## Method
Ordered procedure for handling the task class.

## Failure modes
Common mistakes to avoid.

## Tool hints
Which tools are usually relevant.

## Output expectations
What a good result should contain.

## Stop conditions
When the agent should abstain, hold open, or ask for more data.
```

This is enough for v0.1.

---

# 9. Recommended frontmatter

If you want the runtime to select skills more reliably, add a small structured header.

Example:

```md
---
skill_id: technical_analysis
title: Technical Analysis
domain: finance
use_when:
  - chart analysis
  - trend structure
  - RSI/KDJ/MACD interpretation
avoid_when:
  - no market data available
  - request is purely fundamental
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
```

Then follow with the body.

### Why this helps
Frontmatter allows:
- future skill indexing
- easier runtime selection
- better doc hygiene
- easier testing of skill activation rules

---

# 10. Skill activation model

The thin harness should not load every skill all the time.

Skills should activate **on demand**.

## Step 1 — Task classification
The runtime infers what kind of task this is.

Examples:
- technical analysis
- fundamental analysis
- workflow building
- app scaffolding
- creative prompt design

## Step 2 — Candidate skill selection
The runtime selects one or more candidate skills based on:
- task type
- domain
- keywords
- active worker class
- tool requirements
- operator hint if present

## Step 3 — Skill load
The runtime injects the relevant skill summary or full skill text into the working reasoning path.

## Step 4 — Task execution
The worker and brain use the skill as procedural guidance.

## Step 5 — No permanent merge
The skill does not become global hidden state.
It is activated because the current task needs it.

### Rule
> **Load skills when relevant. Do not wallpaper the runtime with all skills at once.**

---

# 11. Skill selection rules

A skill should be selected only if it materially improves method.

Good reasons to activate a skill:
- recurring domain task
- non-trivial procedure
- repeated failure mode exists
- output quality depends on ordering/checklist logic
- the task needs domain discipline, not just freeform reasoning

Bad reasons to activate a skill:
- decorative symmetry
- because the folder exists
- because the prompt feels too short
- because “more context must be better”

---

# 12. Skill loading strategies

## Strategy A — Full text injection
Load the entire skill into the reasoning context.

### Pros
- simplest
- easiest to debug

### Cons
- token-heavier
- may bloat the prompt if overused

Use for:
- early development
- small skill library
- debugging

---

## Strategy B — Compressed skill summary
Store a compact summary per skill and load that by default.

### Pros
- cheaper
- cleaner runtime

### Cons
- may hide nuance

Use for:
- mature repeated skills
- narrower token budgets

---

## Strategy C — Summary first, full text on escalation
Default to summary.
Load full skill only when:
- ambiguity remains high
- stakes are high
- the worker signals uncertainty
- the result quality needs deeper procedure

### Recommended
This is the best long-term strategy.

---

# 13. Skill interaction with runtime layers

## Brain
The brain may use skill guidance to:
- structure reasoning
- preserve method
- avoid domain drift
- shape final answer better

## Worker
A worker may use skill guidance to:
- order its task steps
- decide what warnings to attach
- decide what output fields matter most

## Tool
A tool should not depend on a skill to do bounded execution.
A tool is execution.
A skill is method guidance.

## Monitor
Monitor may detect that:
- the current answer ignores expected skill method
- output quality is drifting away from known procedure

## Verification
Verification may use skill stop conditions to decide whether a result is complete enough to claim closure.

## Baton
The baton should not contain full skill text.
At most it may carry:
- active skill id
- next hint connected to that skill
- unresolved step tied to the skill

---

# 14. Skill categories for this repo

The roadmap should prioritize skills that match the user’s real workflow.

## 14.1 Finance skills
These are high-value for this runtime.

Examples:
- `technical-analysis.md`
- `fundamental-analysis.md`
- `coin-analysis.md`
- `sector-rotation.md`
- `portfolio-review.md`

### Likely contents
- analysis order
- required inputs
- no-overclaim rules
- what counts as enough evidence
- common traps

---

## 14.2 Builder skills
These match app/web/workflow use cases.

Examples:
- `workflow-builder.md`
- `n8n-builder.md`
- `app-builder.md`
- `repo-refactor.md`
- `runtime-debug.md`

### Likely contents
- step order
- boundary checks
- what to inspect before writing code
- when to stop and verify
- how to avoid architecture drift

---

## 14.3 Creative skills
These match prompt and content workflows.

Examples:
- `creative-prompting.md`
- `image-prompting.md`
- `music-prompting.md`
- `storyboard-design.md`
- `brand-voice.md`

### Likely contents
- prompt structure
- style framing
- composition heuristics
- failure modes like genericness or aesthetic blur

---

## 14.4 Research skills
These help with synthesis-heavy work.

Examples:
- `comparative-research.md`
- `source-triangulation.md`
- `evidence-bounded-summary.md`

### Likely contents
- how to compare sources
- how to bound conclusions
- when to abstain
- how to preserve uncertainty cleanly

---

# 15. Minimal v0.1 skills set

For this repo, a strong starting set would be:

```text
skills/
  technical-analysis.md
  fundamental-analysis.md
  workflow-builder.md
  app-builder.md
  creative-prompting.md
```

This is enough to prove the system without overbuilding it.

---

# 16. Skill authoring rules

A good skill should be:

- short enough to load
- specific enough to matter
- procedural rather than philosophical
- reusable across multiple tasks
- honest about stop conditions
- explicit about failure modes
- clear about which tools are usually relevant

A bad skill is:
- vague
- too broad
- stuffed with lore
- secretly a prompt diary
- full of motivational filler instead of method

---

# 17. Skill stop conditions

Every meaningful skill should include stop conditions.

Examples:
- not enough data
- wrong domain
- tool output missing
- verification gap too large
- ambiguity unresolved
- risk/stakes too high for current evidence

### Why this matters
Without stop conditions, skills become pressure amplifiers:
- they tell the agent how to continue
- but never when to stop

That leads to confident nonsense.

---

# 18. Skill registry (future)

A future thin registry could exist, but should remain small.

Possible path:
`src/skills/registry.py`

It may eventually:
- scan `skills/`
- index metadata/frontmatter
- expose `get_skill(skill_id)`
- rank candidate skills for a task

### Important
Do not build this first.

Start with:
- manual skill files
- explicit selection
- maybe one tiny loader

Registry comes later if needed.

---

# 19. Skill loader (future)

Possible future file:
`src/skills/loader.py`

Its job would be:
- read skill file
- parse frontmatter
- return:
  - full text
  - summary
  - metadata

Again:
- useful later
- not required to prove the concept now

---

# 20. Skill anti-patterns

Avoid these failures.

## Anti-pattern A — Skill as giant prompt dump
A skill should not just be a long wall of instructions with no structure.

## Anti-pattern B — Skill as hidden memory
A skill is not where user/session continuity should be stored.

## Anti-pattern C — Skill as worker substitute
A skill does not execute task logic.
It guides it.

## Anti-pattern D — Skill explosion
Do not create 25 shallow skills with overlapping meaning.
Fewer strong skills are better.

## Anti-pattern E — Always-on skill loading
If every skill is always loaded, the system loses the point of having separable procedural modules.

---

# 21. Recommended implementation phases

## Phase 1 — Static docs only
Create a few real skill files in `skills/`.
Use them manually or by explicit selection.

## Phase 2 — Simple loader
Add a tiny loader that reads a skill file by id.

## Phase 3 — Skill selection hints
Use task type / domain / worker choice to suggest the right skill.

## Phase 4 — Summary + escalation model
Default to summaries, escalate to full skill when needed.

## Phase 5 — Registry and testing
Only if the skill library becomes large enough.

---

# 22. One-line summary

> **Skills are the agent’s reusable playbooks: not actions, not memory, not tools, but procedural knowledge that tells the runtime how to approach recurring classes of task without hardcoding everything into the brain or hiding it inside workers.**
