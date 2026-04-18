# Skill: App Builder

---
skill_id: app_builder
title: App Builder
domain: builder
use_when:
  - app scaffolding
  - small web app planning
  - feature decomposition
  - repo/app structure design
avoid_when:
  - the task is a tiny isolated code snippet only
required_tools: []
optional_tools:
  - filesystem_tool
  - shell_tool
  - package_tool
  - test_runner_tool
tags:
  - app
  - web
  - builder
  - code
---

## Purpose

Use this skill when the task is to design, scaffold, or extend an application rather than answer one coding question.

This skill exists to prevent:
- jumping into code before shape
- writing features without boundaries
- mixing architecture, UI, and execution logic into one blob

---

## Use when

Activate this skill when the user asks for:
- app architecture
- web app scaffolding
- feature planning
- repo structure
- refactor plan
- MVP build steps

---

## Do not use when

Do not use this skill when:
- the task is one small isolated function
- no application structure is involved
- the user only wants high-level product ideation

---

## Inputs expected

Useful inputs:
- app goal
- target users
- MVP scope
- platform (web/mobile/local)
- data sources
- execution/runtime constraints
- what counts as working

---

## Method

### Step 1 — Define the smallest real product
Ask:
- what is the smallest version that proves the idea?
- what can be cut without losing the thesis?
- what is core vs nice-to-have?

---

### Step 2 — Separate layers
At minimum, distinguish:
- UI
- domain logic
- data access
- execution/runtime
- testing/verification

If these are blurred from the start, the repo will rot quickly.

---

### Step 3 — Choose one obvious path
Prefer:
- one clear entrypoint
- one source of truth
- one active architecture path

Avoid:
- multiple competing runtime surfaces
- half-kept legacy
- duplicated logic hidden in adapters

---

### Step 4 — Define contracts before cleverness
Define:
- what goes in
- what comes out
- what each layer owns
- what each layer does not own

This matters more than framework choice early on.

---

### Step 5 — Build thin, then widen
Start with:
- one working vertical slice
- one real flow
- one proof of value

Then widen.

Do not start by building every abstraction the future might need.

---

## Failure modes

Avoid:
- coding before scoping MVP
- mixing repo cleanup and feature build chaotically
- building the plugin system before the core use case works
- keeping multiple entrypoints alive “just in case”
- letting generated code define architecture by accident

---

## Tool hints

Potentially relevant later:
- `filesystem_tool`
- `shell_tool`
- `package_tool`
- `test_runner_tool`

---

## Output expectations

A good output should include:
- app goal
- MVP scope
- layer breakdown
- repo shape
- execution path
- testing / verification path
- what is explicitly out of scope for now

---

## Stop conditions

Hold open when:
- MVP is not defined
- target platform is unclear
- data/external dependencies are unknown
- multiple architecture directions are still equally live
- verification of “working” is undefined

---

## One-line summary

> Scope the smallest real app first, separate layers early, and do not let future abstractions steal the build before the first working slice exists.
