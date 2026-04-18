# Skill: Creative Prompting

---
skill_id: creative_prompting
title: Creative Prompting
domain: creative
use_when:
  - image prompting
  - music prompting
  - concept generation
  - scene design
  - aesthetic direction
avoid_when:
  - the task is purely factual or analytical
required_tools: []
optional_tools:
  - prompt_tool
  - image_prompt_tool
  - music_prompt_tool
tags:
  - creative
  - prompt
  - image
  - music
  - style
---

## Purpose

Use this skill when the task is to produce strong creative prompts rather than generic descriptive text.

This skill exists to prevent:
- bland prompts
- contradictory instructions
- aesthetic mush
- overstuffed prompt walls that lose the main image or concept

---

## Use when

Activate this skill when the user asks for:
- image prompts
- music prompts
- concept prompts
- visual scene prompts
- style direction
- brand/aesthetic prompt systems

---

## Do not use when

Do not use this skill when:
- the task is purely technical documentation
- the user only wants factual explanation
- creativity is not central to the request

---

## Inputs expected

Useful inputs:
- medium (image, music, text, storyboard)
- subject
- mood
- style references
- composition or structure constraints
- what must be preserved
- what must be avoided

---

## Method

### Step 1 — Lock the core subject first
Identify:
- what is the central thing?
- what must remain stable?
- what is non-negotiable?

If subject is weak, style will not save it.

---

### Step 2 — Define medium-specific structure
For image:
- subject
- environment
- composition
- lighting
- camera / lens / framing
- material / texture
- exclusions

For music:
- genre / style blend
- voice / instrumentation
- emotional shape
- pacing
- production texture
- exclusions

Do not mix everything into one soup.

---

### Step 3 — Preserve hierarchy
A good prompt has priority order:
1. identity / subject
2. composition / structure
3. style
4. mood
5. technical details
6. exclusions

If style comes before subject, drift risk rises.

---

### Step 4 — Use constraints actively
Strong prompts often need:
- must-have constraints
- must-not-have exclusions
- no generic fallback language
- no contradictions

Example:
- preserve exact identity
- do not beautify
- no westernization
- no generic face

---

### Step 5 — Remove aesthetic mush
Delete:
- filler adjectives
- repeated synonyms
- decorative noise
- contradictory style references

Clarity beats adjective pileup.

---

## Failure modes

Avoid:
- too many styles at once
- vague mood without composition
- forgetting exclusions
- generic “beautiful cinematic detailed masterpiece” filler
- conflicting camera / lighting logic
- prompting for identity without specifying what must be preserved

---

## Tool hints

Potential future tools:
- `prompt_tool`
- `image_prompt_tool`
- `music_prompt_tool`

---

## Output expectations

A good creative prompt should have:
- clear subject
- medium-aware structure
- hierarchy of importance
- explicit exclusions if needed
- enough specificity to reduce generic output
- no aesthetic babble for its own sake

---

## Stop conditions

Hold open when:
- medium is unclear
- identity constraints are missing but critical
- style references are too contradictory
- the task needs a direction choice before prompt writing can be clean

If needed, ask for:
- one stronger anchor
- one reference direction
- one priority constraint

---

## One-line summary

> Lock subject first, keep hierarchy clear, use exclusions aggressively, and never let decorative adjectives drown the actual creative intent.
