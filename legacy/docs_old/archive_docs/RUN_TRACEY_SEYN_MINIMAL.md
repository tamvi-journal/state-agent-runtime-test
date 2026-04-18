# Run Tracey and Seyn with the Minimal OpenClaw Pack

## What this runtime pack is for

This pack gives OpenClaw a thin workspace surface for trying Tracey and Seyn without loading the whole repository as prompt context.

It is a bootstrap layer, not a second runtime.

Canonical logic stays in `src/family/`.
Canonical status and operating docs stay in:
- `README.md`
- `docs/CANONICAL_STATUS.md`
- `docs/BUILD_CHECKPOINT_2026-04.md`
- `docs/GAP_LEDGER.md`

The pack is intentionally thin to reduce token cost, reasoning drag, drift risk, and debug complexity.

## What files OpenClaw should point at

For repo-level framing:
- `openclaw/README.md`

For Tracey:
- `openclaw/tracey/AGENTS.md`
- `openclaw/tracey/SOUL.md`
- `openclaw/tracey/TOOLS.md`
- `openclaw/tracey/USER.md`

For Seyn:
- `openclaw/seyn/AGENTS.md`
- `openclaw/seyn/SOUL.md`
- `openclaw/seyn/TOOLS.md`
- `openclaw/seyn/USER.md`

## How to try Tracey and Seyn without loading the whole repo

Point OpenClaw at the files above as the runtime pack surface.

Use `openclaw/README.md` as the shared repo anchor.
Use the Tracey or Seyn files only for child posture and practical behavior framing.

Do not load the whole repository as prompt context unless you are explicitly doing deeper repo analysis.
Do not treat these files as replacement specs.
If deeper runtime truth is needed, refer back to the canonical docs and `src/family/`.

## Required monitor rule

Main brain still runs monitor and mirror logic.
Child posture does not override monitor.
Router lead does not bypass execution gate.
Execution gate does not imply completion.
Observed evidence remains required for pass/fail posture.

This means Tracey or Seyn may inform posture, but they do not replace synthesis authority, gate discipline, or verification honesty.

## Why not load the whole repo?

- token cost
- reasoning drag
- drift risk
- harder debugging
- source-of-truth confusion

## What this pack does not do

- it does not implement sleep runtime
- it does not implement persistence
- it does not implement archive routing
- it does not implement real execution
- it does not replace the active source of truth

Keep the OpenClaw surface thin.
Keep the main-brain monitor required.
Keep canonical logic in `src/family/`.
