# Phase 5.3 — Cross-Logic Bridge / Reconciliation Protocol

This pack adds a protocol for moving from disagreement to meaningful convergence
without forcing fake reconciliation.

## Files
- `src/family/cross_logic_exchange.py`
- `src/family/reconciliation_protocol.py`
- `tests/test_reconciliation_protocol.py`

## Goal
Support four outcomes:
- remain_open
- temporary_operational_alignment
- partial_convergence
- full_convergence

And enforce:
- no full convergence without mutual logic visibility
- operational alignment != epistemic convergence
- partial convergence preserves open residue

## Run
```powershell
$env:PYTHONPATH = "src"
pytest -q
```
