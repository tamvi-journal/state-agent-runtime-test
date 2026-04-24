from __future__ import annotations

from typing import Any

from state_memory.contracts import StateMemoryRecord


def records_from_wake_result(
    *,
    wake_result: dict[str, Any] | None,
    session_id: str = "",
    scope: str = "runtime/wake",
) -> list[StateMemoryRecord]:
    if not wake_result:
        return []
    resume_class = str(wake_result.get("resume_class", "none"))
    if resume_class in {"none", "full_resume"}:
        return []

    event_type = {
        "degraded_resume": "wake_degraded",
        "clarify_first": "wake_clarify_first",
        "blocked": "wake_blocked",
    }.get(resume_class, "generic_state_event")
    summary = str(wake_result.get("summary", "")).strip() or f"wake result classified as {resume_class}"
    constraints = dict(wake_result.get("constraints", {}))
    return [
        StateMemoryRecord(
            event_type=event_type,  # type: ignore[arg-type]
            scope=scope,
            session_id=session_id,
            summary=summary,
            source="wake_sanity",
            lifecycle_status="observed",
            evidence={
                "resume_class": resume_class,
                "checks": dict(wake_result.get("checks", {})),
                "requires_revalidation": list(constraints.get("requires_revalidation", [])),
                "forbidden_claims": list(constraints.get("forbidden_claims", [])),
            },
            tags=["wake", resume_class],
        )
    ]


def records_from_delta(
    *,
    delta: dict[str, Any],
    session_id: str = "",
    scope: str = "runtime/delta",
) -> list[StateMemoryRecord]:
    records: list[StateMemoryRecord] = []
    if bool(delta.get("repair_event", False)):
        records.append(
            StateMemoryRecord(
                event_type="repair_event",
                scope=scope,
                session_id=session_id,
                summary="repair event observed in runtime delta",
                source="delta_log",
                lifecycle_status="observed",
                evidence=dict(delta),
                tags=["repair", str(delta.get("trigger_cue", ""))],
            )
        )
    coherence_shift = float(delta.get("coherence_shift", 0.0) or 0.0)
    if coherence_shift < 0:
        records.append(
            StateMemoryRecord(
                event_type="coherence_drop",
                scope=scope,
                session_id=session_id,
                summary=f"coherence shifted by {coherence_shift}",
                source="delta_log",
                lifecycle_status="observed",
                evidence=dict(delta),
                tags=["coherence", "drop"],
            )
        )
    mode_shift = str(delta.get("mode_shift", "")).strip()
    if mode_shift:
        records.append(
            StateMemoryRecord(
                event_type="mode_shift",
                scope=scope,
                session_id=session_id,
                summary=f"mode shifted: {mode_shift}",
                source="delta_log",
                lifecycle_status="observed",
                evidence=dict(delta),
                tags=["mode", mode_shift],
            )
        )
    return records


def records_from_tracey_turn(
    *,
    tracey_turn: dict[str, Any] | None,
    session_id: str = "",
    scope: str = "tracey/runtime",
) -> list[StateMemoryRecord]:
    if not tracey_turn:
        return []
    records: list[StateMemoryRecord] = []
    for anchor in tracey_turn.get("reactivated_anchors", []) or []:
        anchor_id = str(anchor.get("anchor_id", "")).strip()
        if not anchor_id:
            continue
        records.append(
            StateMemoryRecord(
                event_type="anchor_reactivation",
                scope=scope,
                session_id=session_id,
                summary=f"Tracey anchor reactivated: {anchor_id}",
                source="tracey_turn",
                lifecycle_status="observed",
                evidence={"anchor": dict(anchor)},
                tags=["tracey", "anchor", anchor_id],
            )
        )
    response_hints = dict(tracey_turn.get("response_hints", {}))
    if str(response_hints.get("tone_constraint", "")) in {"wake_degraded", "wake_clarify_first", "wake_blocked"}:
        records.append(
            StateMemoryRecord(
                event_type="verification_boundary",
                scope=scope,
                session_id=session_id,
                summary=f"Tracey wake posture constrained by {response_hints.get('tone_constraint')}",
                source="tracey_turn",
                lifecycle_status="observed",
                evidence=response_hints,
                tags=["tracey", "wake", str(response_hints.get("resume_class", ""))],
            )
        )
    return records


def records_from_turn(
    *,
    wake_result: dict[str, Any] | None = None,
    delta: dict[str, Any] | None = None,
    tracey_turn: dict[str, Any] | None = None,
    session_id: str = "",
) -> list[StateMemoryRecord]:
    records: list[StateMemoryRecord] = []
    records.extend(records_from_wake_result(wake_result=wake_result, session_id=session_id))
    if delta:
        records.extend(records_from_delta(delta=delta, session_id=session_id))
    records.extend(records_from_tracey_turn(tracey_turn=tracey_turn, session_id=session_id))
    return records
