#!/usr/bin/env python3
"""Run the Phase 9 deterministic boundary-awareness demo scenarios."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.scenario_runner import render_report, run_scenarios


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic boundary-awareness scenarios")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=None,
        help="Optional path to boundary_scenarios.json",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output instead of readable report",
    )
    args = parser.parse_args()

    report = run_scenarios(path=args.fixtures)
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(render_report(report), end="")


if __name__ == "__main__":
    main()
