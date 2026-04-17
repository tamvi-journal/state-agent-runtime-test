from __future__ import annotations

from pathlib import Path


def test_local_smoke_docs_exist() -> None:
    expected = [
        Path("docs/LOCAL_SMOKE_TEST_CHECKLIST.md"),
        Path("docs/LOCAL_EXPECTED_OUTPUTS.md"),
        Path("docs/LOCAL_TROUBLESHOOTING.md"),
        Path("scripts/local_smoke_test.ps1"),
        Path("scripts/local_smoke_test.sh"),
    ]

    missing = [str(p) for p in expected if not p.exists()]
    assert not missing, f"Missing expected local smoke files: {missing}"
