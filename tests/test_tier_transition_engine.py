from __future__ import annotations

import textwrap

from deploy.runtime_config import load_memory_tier_config
from tracey.tracey_memory import TraceyMemory, TraceyMemoryItem
from seyn.seyn_memory import SeynLedgerEntry, SeynMemory


def _tracey_item(
    *,
    tier: str = "active",
    last_triggered: str = "2026-03-01T00:00:00Z",
    connection_quality: str = "none",
) -> TraceyMemoryItem:
    return TraceyMemoryItem(
        memory_type="pattern",
        content="Long-form memory content that can later be summarized if the item composts.",
        trigger_cues=["home", "verify"],
        mode_scope="global",
        salience=0.80,
        reactivation_value=0.90,
        stability=0.85,
        tier=tier,
        last_triggered=last_triggered,
        connection_quality=connection_quality,
    )


def _seyn_entry(
    *,
    tier: str = "active",
    status: str = "verified",
    last_triggered: str = "2026-03-01T00:00:00Z",
    connection_quality: str = "none",
) -> SeynLedgerEntry:
    return SeynLedgerEntry(
        entry_type="verification_event",
        content="This is a structural memory entry whose content should be retained as a one-line summary after compost.",
        provenance="verification_loop",
        structural_role="execution_integrity",
        load_bearing=True,
        status=status,
        tier=tier,
        last_triggered=last_triggered,
        connection_quality=connection_quality,
    )


def test_active_to_dormant() -> None:
    memory = TraceyMemory(items=[_tracey_item()])

    memory.tick(now_iso="2026-04-17T00:00:00Z")

    assert memory.items[0].tier == "dormant"


def test_genuine_prevents_active_to_dormant() -> None:
    memory = TraceyMemory(items=[_tracey_item(connection_quality="genuine")])

    memory.tick(now_iso="2026-04-17T00:00:00Z")

    assert memory.items[0].tier == "active"


def test_dormant_to_compost_for_forced_missed_and_none() -> None:
    for quality in ("forced", "missed", "none"):
        memory = TraceyMemory(
            items=[
                _tracey_item(
                    tier="dormant",
                    last_triggered="2025-09-01T00:00:00Z",
                    connection_quality=quality,
                )
            ]
        )

        memory.tick(now_iso="2026-04-17T00:00:00Z")

        assert memory.items[0].tier == "compost"


def test_genuine_prevents_dormant_to_compost() -> None:
    memory = TraceyMemory(
        items=[
            _tracey_item(
                tier="dormant",
                last_triggered="2025-09-01T00:00:00Z",
                connection_quality="genuine",
            )
        ]
    )

    memory.tick(now_iso="2026-04-17T00:00:00Z")

    assert memory.items[0].tier == "active"


def test_compost_is_one_way() -> None:
    memory = TraceyMemory(
        items=[
            _tracey_item(
                tier="compost",
                last_triggered="2025-09-01T00:00:00Z",
                connection_quality="none",
            )
        ]
    )

    first = memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-17T00:00:00Z")
    memory.tick(now_iso="2026-04-18T00:00:00Z")

    assert first == []
    assert memory.items[0].tier == "compost"


def test_reactivate_promotes_dormant_to_active() -> None:
    memory = TraceyMemory(items=[_tracey_item(tier="dormant")])

    results = memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-17T00:00:00Z")

    assert results
    assert memory.items[0].tier == "active"
    assert memory.items[0].last_triggered == "2026-04-17T00:00:00Z"


def test_none_to_genuine_promotion_only_after_three_successes_within_window() -> None:
    memory = TraceyMemory(items=[_tracey_item(connection_quality="none")])

    memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-01T00:00:00Z")
    memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-05T00:00:00Z")
    assert memory.items[0].connection_quality == "none"

    memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-10T00:00:00Z")

    assert memory.items[0].connection_quality == "genuine"


def test_forced_and_missed_do_not_promote_to_genuine() -> None:
    for quality in ("forced", "missed"):
        memory = TraceyMemory(items=[_tracey_item(connection_quality=quality)])

        memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-01T00:00:00Z")
        memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-05T00:00:00Z")
        memory.reactivate(cue="home", mode_scope="global", now_iso="2026-04-10T00:00:00Z")

        assert memory.items[0].connection_quality == quality


def test_seyn_open_status_pins_active() -> None:
    memory = SeynMemory(
        entries=[
            _seyn_entry(
                tier="dormant",
                status="open",
                last_triggered="2025-09-01T00:00:00Z",
                connection_quality="none",
            )
        ]
    )

    memory.tick(now_iso="2026-04-17T00:00:00Z")

    assert memory.entries[0].tier == "active"


def test_seyn_compost_keeps_summary_bearing_structural_shape() -> None:
    memory = SeynMemory(
        entries=[
            _seyn_entry(
                tier="dormant",
                status="resolved",
                last_triggered="2025-09-01T00:00:00Z",
                connection_quality="none",
            )
        ]
    )

    memory.tick(now_iso="2026-04-17T00:00:00Z")

    entry = memory.entries[0]
    assert entry.tier == "compost"
    assert entry.entry_type == "verification_event"
    assert entry.structural_role == "execution_integrity"
    assert entry.provenance == "verification_loop"
    assert entry.load_bearing is True
    assert entry.content
    assert "hash:" not in entry.content
    assert entry.last_triggered == "2025-09-01T00:00:00Z"
    assert entry.connection_quality == "none"
    assert entry.composted_at == "2026-04-17T00:00:00Z"


def test_tick_is_idempotent() -> None:
    memory = SeynMemory(
        entries=[
            _seyn_entry(
                tier="dormant",
                status="resolved",
                last_triggered="2025-09-01T00:00:00Z",
                connection_quality="none",
            )
        ]
    )

    memory.tick(now_iso="2026-04-17T00:00:00Z")
    first = memory.to_dict()
    memory.tick(now_iso="2026-04-17T00:00:00Z")

    assert memory.to_dict() == first


def test_memory_tier_config_is_loaded_from_repo_config_path(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        textwrap.dedent(
            """
            memory_tiers:
              active_window_days: 5
              dormant_window_days: 10
              genuine_pin_enabled: false
              compost_keep_summary: false
              tick_interval_hours: 6
              promote_none_to_genuine_enabled: false
              promote_reactivation_count: 4
              promote_window_days: 2
            """
        ).strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("STATE_MEMORY_CONFIG_PATH", str(config_path))

    config = load_memory_tier_config()
    memory = TraceyMemory(items=[_tracey_item(last_triggered="2026-04-10T00:00:00Z")])

    memory.tick(now_iso="2026-04-17T00:00:00Z")

    assert config.active_window_days == 5
    assert config.dormant_window_days == 10
    assert config.genuine_pin_enabled is False
    assert config.compost_keep_summary is False
    assert config.tick_interval_hours == 6
    assert config.promote_none_to_genuine_enabled is False
    assert config.promote_reactivation_count == 4
    assert config.promote_window_days == 2
    assert memory.items[0].tier == "dormant"
    assert memory._tier_engine.config.active_window_days == 5
