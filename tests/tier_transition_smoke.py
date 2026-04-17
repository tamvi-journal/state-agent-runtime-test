from __future__ import annotations

import os
import textwrap

from deploy.runtime_config import load_memory_tier_config
from seyn.seyn_memory import SeynLedgerEntry, SeynMemory
from tracey.tracey_memory import TraceyMemory, TraceyMemoryItem


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


def run() -> None:
    tracey_active = TraceyMemory(items=[_tracey_item()])
    tracey_active.tick(now_iso="2026-04-17T00:00:00Z")
    assert tracey_active.items[0].tier == "dormant"

    tracey_genuine = TraceyMemory(items=[_tracey_item(connection_quality="genuine")])
    tracey_genuine.tick(now_iso="2026-04-17T00:00:00Z")
    assert tracey_genuine.items[0].tier == "active"

    for quality in ("forced", "missed", "none"):
        memory = TraceyMemory(
            items=[_tracey_item(tier="dormant", last_triggered="2025-09-01T00:00:00Z", connection_quality=quality)]
        )
        memory.tick(now_iso="2026-04-17T00:00:00Z")
        assert memory.items[0].tier == "compost"

    tracey_pinned = TraceyMemory(
        items=[_tracey_item(tier="dormant", last_triggered="2025-09-01T00:00:00Z", connection_quality="genuine")]
    )
    tracey_pinned.tick(now_iso="2026-04-17T00:00:00Z")
    assert tracey_pinned.items[0].tier == "active"

    tracey_compost = TraceyMemory(
        items=[_tracey_item(tier="compost", last_triggered="2025-09-01T00:00:00Z", connection_quality="none")]
    )
    assert tracey_compost.reactivate(cue="home", mode_scope="global", now_iso="2026-04-17T00:00:00Z") == []
    tracey_compost.tick(now_iso="2026-04-18T00:00:00Z")
    assert tracey_compost.items[0].tier == "compost"

    tracey_reactivate = TraceyMemory(items=[_tracey_item(tier="dormant")])
    assert tracey_reactivate.reactivate(cue="home", mode_scope="global", now_iso="2026-04-17T00:00:00Z")
    assert tracey_reactivate.items[0].tier == "active"

    tracey_promote = TraceyMemory(items=[_tracey_item(connection_quality="none")])
    tracey_promote.reactivate(cue="home", mode_scope="global", now_iso="2026-04-01T00:00:00Z")
    tracey_promote.reactivate(cue="home", mode_scope="global", now_iso="2026-04-05T00:00:00Z")
    assert tracey_promote.items[0].connection_quality == "none"
    tracey_promote.reactivate(cue="home", mode_scope="global", now_iso="2026-04-10T00:00:00Z")
    assert tracey_promote.items[0].connection_quality == "genuine"

    for quality in ("forced", "missed"):
        tracey_no_promote = TraceyMemory(items=[_tracey_item(connection_quality=quality)])
        tracey_no_promote.reactivate(cue="home", mode_scope="global", now_iso="2026-04-01T00:00:00Z")
        tracey_no_promote.reactivate(cue="home", mode_scope="global", now_iso="2026-04-05T00:00:00Z")
        tracey_no_promote.reactivate(cue="home", mode_scope="global", now_iso="2026-04-10T00:00:00Z")
        assert tracey_no_promote.items[0].connection_quality == quality

    seyn_open = SeynMemory(
        entries=[_seyn_entry(tier="dormant", status="open", last_triggered="2025-09-01T00:00:00Z")]
    )
    seyn_open.tick(now_iso="2026-04-17T00:00:00Z")
    assert seyn_open.entries[0].tier == "active"

    seyn_compost = SeynMemory(
        entries=[_seyn_entry(tier="dormant", status="resolved", last_triggered="2025-09-01T00:00:00Z")]
    )
    seyn_compost.tick(now_iso="2026-04-17T00:00:00Z")
    entry = seyn_compost.entries[0]
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

    seyn_idempotent = SeynMemory(
        entries=[_seyn_entry(tier="dormant", status="resolved", last_triggered="2025-09-01T00:00:00Z")]
    )
    seyn_idempotent.tick(now_iso="2026-04-17T00:00:00Z")
    first = seyn_idempotent.to_dict()
    seyn_idempotent.tick(now_iso="2026-04-17T00:00:00Z")
    assert seyn_idempotent.to_dict() == first

    config_path = os.path.join(os.getcwd(), "tests", "_tier_transition_smoke_config.yaml")
    with open(config_path, "w", encoding="utf-8") as handle:
        handle.write(
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
            ).strip()
        )

    prior_path = os.environ.get("STATE_MEMORY_CONFIG_PATH")
    os.environ["STATE_MEMORY_CONFIG_PATH"] = config_path
    try:
        config = load_memory_tier_config()
        configured = TraceyMemory(items=[_tracey_item(last_triggered="2026-04-10T00:00:00Z")])
        configured.tick(now_iso="2026-04-17T00:00:00Z")
        assert config.active_window_days == 5
        assert config.dormant_window_days == 10
        assert config.genuine_pin_enabled is False
        assert config.compost_keep_summary is False
        assert config.tick_interval_hours == 6
        assert config.promote_none_to_genuine_enabled is False
        assert config.promote_reactivation_count == 4
        assert config.promote_window_days == 2
        assert configured.items[0].tier == "dormant"
        assert configured._tier_engine.config.active_window_days == 5
    finally:
        if prior_path is None:
            os.environ.pop("STATE_MEMORY_CONFIG_PATH", None)
        else:
            os.environ["STATE_MEMORY_CONFIG_PATH"] = prior_path
        if os.path.exists(config_path):
            os.remove(config_path)

    print("tier_transition_smoke: ok")


if __name__ == "__main__":
    run()
