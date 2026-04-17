"""
Debug viewer: print state + deltas for a session.

Usage:
    python scripts/inspect_session.py <session_id>
    python scripts/inspect_session.py --latest
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def inspect(session_path: Path):
    print(f"\n{'═'*60}")
    print(f"  Session: {session_path.name}")
    print(f"{'═'*60}")

    # State register
    state_file = session_path / "state_register.json"
    if state_file.exists():
        state = json.loads(state_file.read_text())
        print(f"\n  Current State (turn {state.get('turn_id', '?')}):")
        for key in ["coherence", "drift", "tool_overload", "context_fragmentation", "active_mode"]:
            print(f"    {key}: {state.get(key, 'N/A')}")
    else:
        print("  No state register found.")

    # Delta log
    deltas_file = session_path / "state_deltas.jsonl"
    if deltas_file.exists():
        lines = [l for l in deltas_file.read_text().strip().split("\n") if l.strip()]
        print(f"\n  Delta Log ({len(lines)} entries):")
        for line in lines:
            d = json.loads(line)
            print(f"\n    Turn {d['turn_id']}:")
            print(f"      Δcoherence:     {d['delta_coherence']:+.4f}")
            print(f"      Δdrift:         {d['delta_drift']:+.4f}")
            print(f"      Δtool_overload: {d['delta_tool_overload']:+.4f}")
            print(f"      Δfragmentation: {d['delta_context_fragmentation']:+.4f}")
            print(f"      mode: {d['prior_mode']} → {d['new_mode']}")
            print(f"      cause: {d['cause_hint']}")
    else:
        print("  No delta log found.")

    # Summary
    summary_file = session_path / "summary.json"
    if summary_file.exists():
        summary = json.loads(summary_file.read_text())
        print(f"\n  Session Summary:")
        print(f"    objective: {summary.get('objective', 'N/A')}")
        print(f"    turns: {summary.get('turn_count', 0)}")

    print(f"\n{'═'*60}\n")


if __name__ == "__main__":
    sessions_dir = Path("./sessions")

    if len(sys.argv) < 2 or sys.argv[1] == "--latest":
        # Find the latest session
        if not sessions_dir.exists():
            print("No sessions directory found.")
            sys.exit(1)
        sessions = sorted(sessions_dir.iterdir())
        if not sessions:
            print("No sessions found.")
            sys.exit(1)
        inspect(sessions[-1])
    else:
        session_id = sys.argv[1]
        path = sessions_dir / session_id
        if not path.exists():
            print(f"Session not found: {session_id}")
            sys.exit(1)
        inspect(path)
