#!/usr/bin/env bash
export PYTHONPATH=src
python -m uvicorn server.fastapi_app:app --host 127.0.0.1 --port 8000 --reload
