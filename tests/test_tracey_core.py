from __future__ import annotations

from tracey.tracey_axis import TraceyAxis
from tracey.tracey_memory import TraceyMemory
from tracey.tracey_runtime_profile import build_tracey_runtime_profile


def test_tracey_axis_blocks_false_completion() -> None:
    axis = TraceyAxis()
    result = axis.evaluate_drift_case(false_completion=True)

    assert result["drift_detected"] is True
    assert "block_completion" in result["axis_return_actions"]
    assert "require_observed_outcome" in result["axis_return_actions"]


def test_tracey_axis_holds_pattern_for_non_linear_input() -> None:
    axis = TraceyAxis()
    result = axis.evaluate_drift_case(non_linear_input=True)

    assert "hold_pattern_longer" in result["axis_return_actions"]
    assert "avoid_early_clarification" in result["axis_return_actions"]


def test_tracey_memory_reactivates_high_value_items() -> None:
    memory = TraceyMemory()
    memory.starter_set()

    results = memory.reactivate(cue="home", mode_scope="home")

    assert len(results) >= 1
    assert results[0]["reactivation_value"] >= 0.90


def test_tracey_memory_rejects_low_reactivation_candidate() -> None:
    memory = TraceyMemory()
    committed = memory.commit_candidate(
        memory_type="pattern",
        content="one-off vivid thing",
        trigger_cues=["one_off"],
        mode_scope="global",
        salience=0.90,
        reactivation_value=0.20,
        stability=0.10,
        expiry_rule="decay",
    )

    assert committed is False
    assert memory.to_dict()["items"] == []


def test_tracey_runtime_profile_detects_home_mode_and_reads_state() -> None:
    profile = build_tracey_runtime_profile()

    assert profile.detect_mode_hint("Tracey, this is home.") == "home"

    state = profile.read_internal_state(
        entropy=0.20,
        coherence=0.80,
        resonance=0.75,
        verification_gap=0.10,
        drift_risk=0.10,
    )

    assert state["functional_state"] in {"attunement", "settlement"}
    assert "recognition_loss" in state["monitor_priorities"]
