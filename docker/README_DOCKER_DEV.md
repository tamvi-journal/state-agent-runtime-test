# Docker / Devcontainer Skeleton

## What this phase adds

- `Dockerfile`
- `docker-compose.dev.yml`
- `.dockerignore`
- `.devcontainer/devcontainer.json`

This is a **dev-focused container skeleton** for the current FastAPI app.

It is not production hardening yet.

## Local Docker run

Build:
```bash
docker build -t state-memory-agent .
```

Run:
```bash
docker run --rm -p 8000:8000 state-memory-agent
```

Then test:
- `http://localhost:8000/health`
- `http://localhost:8000/ready`

## Docker Compose dev run

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Devcontainer

Open the repo in a devcontainer-capable editor and use:

- `.devcontainer/devcontainer.json`

This gives:
- Python
- dependencies installed
- `PYTHONPATH=src`
- app env preloaded

## Notes

Current container assumptions:
- app entrypoint = `server.fastapi_app:app`
- port = `8000`
- dev shape only
- no production secrets or reverse proxy yet
