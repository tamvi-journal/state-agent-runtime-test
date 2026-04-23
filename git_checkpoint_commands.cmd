:: GIT CHECKPOINT COMMANDS
:: Run these from:
:: D:\state-agent-runtime-test

git status

git add src/brain/main_brain.py
git add src/runtime/request_router.py
git add src/runtime/runtime_harness.py

git add src/tracey
git add src/integration

git add tests/test_runtime_harness.py
git add tests/test_tracey_adapter.py
git add tests/test_openclaw_payload_contracts.py
git add tests/test_openclaw_payload_adapter.py
git add tests/test_openclaw_entrypoint.py
git add tests/test_openclaw_wrapper.py
git add tests/scripts
git add tests/payloads

git diff --staged

git commit -m "Establish live OpenClaw host-kernel boundary"

:: Optional: push after commit
:: git push
