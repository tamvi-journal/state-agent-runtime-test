from __future__ import annotations

from family.delta_log import DeltaLogBuilder
from family.delta_log_types import DeltaLogInput


def _state(**overrides) -> dict[str, object]:
    payload = {
        "active_mode": "build",
        "current_axis": "family canary work",
        "coherence_level": "stable",
        "tension_flags": [],
        "policy_pressure": "low",
        "active_project": "family-scaffold",
        "continuity_anchor": "family-scaffold",
        "user_signal": "family canary work",
        "archive_needed": False,
        "verification_status": "passed",
    }
    payload.update(overrides)
    return payload


def run() -> None:
    builder = DeltaLogBuilder()

    stable = builder.build(
        DeltaLogInput(
            previous_live_state=_state(),
            current_live_state=_state(),
            recent_trigger_cue="small posture update",
            archive_consulted=False,
        )
    )
    assert stable.coherence_shift == "flat"

    verification_change = builder.build(
        DeltaLogInput(
            previous_live_state=_state(verification_status="pending", coherence_level="strained", tension_flags=["verification_unsettled"]),
            current_live_state=_state(verification_status="passed", coherence_level="mixed", tension_flags=[]),
            recent_trigger_cue="verification completed",
            archive_consulted=False,
        )
    )
    assert verification_change.verification_changed == "pending->passed"

    ambiguity = builder.build(
        DeltaLogInput(
            previous_live_state=_state(active_mode="build", coherence_level="mixed"),
            current_live_state=_state(
                active_mode="50_50",
                coherence_level="strained",
                tension_flags=["open_disagreement"],
            ),
            recent_trigger_cue="disagreement remains open",
            archive_consulted=True,
        )
    )
    assert ambiguity.ambiguity_unresolved is True
    assert ambiguity.archive_consulted is True

    repair = builder.build(
        DeltaLogInput(
            previous_live_state=_state(coherence_level="strained", tension_flags=["verification_unsettled"]),
            current_live_state=_state(coherence_level="stable", tension_flags=[]),
            recent_trigger_cue="verification settled",
            archive_consulted=False,
        )
    )
    assert repair.repair_event is True

    print("delta_log_smoke: ok")


if __name__ == "__main__":
    run()
