# Phase 7.3 — Docker / Devcontainer Skeleton

This pack adds the first container/dev-environment packaging layer.

## Files
- `Dockerfile`
- `docker-compose.dev.yml`
- `.dockerignore`
- `.devcontainer/devcontainer.json`
- `docker/README_DOCKER_DEV.md`

## Goal
Move from:
- local bootstrap scripts
- local app wiring

to:
- repeatable containerized dev environment
- repeatable devcontainer environment

Still excluded:
- no production Docker hardening
- no nginx/reverse proxy
- no process supervisor
- no deployment platform descriptor

## Typical run
```bash
docker compose -f docker-compose.dev.yml up --build
```
