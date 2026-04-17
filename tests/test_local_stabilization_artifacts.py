from __future__ import annotations

from pathlib import Path


def test_local_stabilization_files_exist() -> None:
    expected = [
        Path("data/sample_market_data.csv"),
        Path("config/local.runtime.env.example"),
        Path("scripts/run_local_validation.ps1"),
        Path("scripts/run_local_validation.sh"),
        Path("docs/LOCAL_OPENCLAW_COOKBOOK.md"),
        Path("docs/LOCAL_STABILIZATION_NOTES.md"),
    ]
    missing = [str(p) for p in expected if not p.exists()]
    assert not missing, f"Missing expected stabilization files: {missing}"
