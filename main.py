from __future__ import annotations

import json
import sys

from runtime.runtime_harness import RuntimeHarness


DEMO_REQUESTS = (
    "hello there",
    "Load MBB daily data",
    "Load VCB daily data",
)


def run_demo() -> int:
    harness = RuntimeHarness()
    baton = None

    for index, user_text in enumerate(DEMO_REQUESTS, start=1):
        result = harness.run(user_text=user_text, baton=baton, render_mode="builder")
        baton = result["handoff_baton"]

        print(f"\n=== TURN {index} ===")
        print(f"User: {user_text}")
        print(f"Gate: {result['gate_decision']}")
        print(f"Monitor: {result['monitor_summary']}")
        print(f"Verification: {result['verification_record']}")
        print("Response:")
        print(result["final_response"])
        print("Baton:")
        print(json.dumps(result["handoff_baton"], indent=2))

    return 0


def run_once(user_text: str) -> int:
    harness = RuntimeHarness()
    result = harness.run(user_text=user_text, render_mode="user")

    print(result["final_response"])
    print("\nHandoff baton:")
    print(json.dumps(result["handoff_baton"], indent=2))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python main.py demo')
        print('  python main.py run "Load MBB daily data"')
        raise SystemExit(0)

    command = sys.argv[1].lower()
    if command == "demo":
        raise SystemExit(run_demo())
    if command == "run":
        if len(sys.argv) < 3:
            raise SystemExit("Provide a request string after 'run'.")
        raise SystemExit(run_once(" ".join(sys.argv[2:])))

    raise SystemExit(f"Unknown command: {command}")
