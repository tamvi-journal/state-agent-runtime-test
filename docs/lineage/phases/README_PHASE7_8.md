# Phase 7.8 — Local Run Validation Pass / Smoke Test Checklist

This pack adds the first practical local validation layer.

## Files
- `docs/LOCAL_SMOKE_TEST_CHECKLIST.md`
- `docs/LOCAL_EXPECTED_OUTPUTS.md`
- `docs/LOCAL_TROUBLESHOOTING.md`
- `scripts/local_smoke_test.ps1`
- `scripts/local_smoke_test.sh`
- `tests/test_local_smoke_docs_presence.py`

## Goal
Move from:
- buildable local app

to:
- locally testable app with a repeatable smoke-test path

This phase does not change runtime capability.
It makes local validation easier and more repeatable.
