#!/usr/bin/env bash
set -e
export PYTHONPATH=src

echo "== dependency sanity =="
python -c "import fastapi, uvicorn, httpx; print('deps-ok')"

echo "== runtime provider sanity =="
python -c "from server.runtime_provider import RuntimeProvider; r=RuntimeProvider().get_runtime_result(user_text='Tracey, this is home, but verify whether MBB daily data is actually done.'); print({'has_final_response': 'final_response' in r, 'sample_data_path': r.get('sample_data_path')})"

echo "== test suite =="
pytest -q
