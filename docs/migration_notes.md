# Migration Notes

This repo previously used `docs/` as a storage dump for archived source code, server modules, family-runtime code, memory systems, and scaffold leftovers.

That layout has been corrected.

## Current Rule

`docs/` now contains documents only.

Allowed content here:

- architecture notes
- runbooks
- boundaries
- migration notes
- other human-facing documentation files

## Legacy Rule

Historical code and non-document artifacts now live under `legacy/`.

Examples:

- old family runtime code
- Tracey and Seyn modules
- old server and transport layers
- old memory runtime code
- app v1 scaffold
- historical docs and schemas retained for reference

`legacy/` is not part of the active runtime path.
