# Boundaries

## Hard Runtime Rules

### Main Brain Law

The main brain is the final synthesis authority.
Helpers, workers, adapters, and traces are evidence sources only.

### Gate Law

All meaningful actions must go through the gate.
There is no direct execution bypass in the active runtime path.

### Verification Law

The system must not mark work done from:

- intent alone
- execution text alone
- tool success language alone

Only observed outcome can support a verified result.

### Monitor Law

The monitor stays small and operational.
It does not become a second planner or router.

### Memory Law

Active memory is limited to the compact baton.
There is no active archive-driven memory path.
There is no checkpoint/tier memory path.

### Handoff Law

The baton contains only:

- `task_focus`
- `active_mode`
- `open_loops`
- `verification_status`
- `monitor_summary`
- `next_hint`

Transcript replay is out of bounds.

### OpenClaw Pack Law

The OpenClaw pack is a formatting surface only.
It may adapt requests into the harness, but it must not contain hidden runtime logic.

## Repo Boundaries

Active code lives under `src/` in the thin runtime modules.

Reference and archived material lives under:

- `docs/reference/`
- `docs/archive/`

If a builder needs family-runtime history, they should read it from those docs, not wire it back into the active path.
