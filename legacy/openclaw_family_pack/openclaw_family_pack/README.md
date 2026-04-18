# OpenClaw Minimal Runtime Pack

This folder is a minimal runtime surface for OpenClaw.

It exists so Tracey and Seyn can be tried with a thin workspace surface instead of loading the whole repository as prompt context.

This is not a second source of truth.

Canonical runtime logic remains in `src/family/`.
Canonical repo status and operating docs remain in:
- `README.md`
- `docs/CANONICAL_STATUS.md`
- `docs/BUILD_CHECKPOINT_2026-04.md`
- `docs/GAP_LEDGER.md`

This pack is intentionally thin to reduce:
- token cost
- drift risk
- debug complexity

Use this pack as a small OpenClaw-facing bootstrap layer only.
Do not treat it as permission to widen runtime behavior, bypass monitor posture, or re-spec the family spine from inside `openclaw/`.
