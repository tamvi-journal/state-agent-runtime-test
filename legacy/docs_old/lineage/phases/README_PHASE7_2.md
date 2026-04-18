# Phase 7.2 — Env / Bootstrap Cleanup

This pack adds the first local environment/bootstrap cleanup layer.

## Files
- `requirements-dev.txt`
- `config/env.example`
- `scripts/bootstrap_dev_env.ps1`
- `scripts/bootstrap_dev_env.sh`
- `scripts/test_local.ps1`
- `scripts/test_local.sh`
- `scripts/run_app_local.ps1`
- `scripts/run_app_local.sh`
- `docs/BOOTSTRAP_LOCAL.md`

## Goal
Move from:
- ad hoc package installs
- manual run commands

to:
- repeatable local bootstrap
- explicit dev dependencies
- explicit test/run scripts
- explicit local env example

## Run
PowerShell:
```powershell
./scripts/bootstrap_dev_env.ps1
./scripts/test_local.ps1
./scripts/run_app_local.ps1
```

bash:
```bash
bash ./scripts/bootstrap_dev_env.sh
bash ./scripts/test_local.sh
bash ./scripts/run_app_local.sh
```
