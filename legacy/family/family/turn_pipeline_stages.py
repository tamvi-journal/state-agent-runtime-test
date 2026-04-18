from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from family.disagreement_types import DisagreementEvent
from family.effort_types import EffortInput
from family.execution_request_classifier import ExecutionRequestClassifier
from family.execution_types import ExecutionRequest
from family.turn_handoff_types import TurnHandoff
from family.turn_pipeline_types import FamilyTurnInput
from family.verification_loop import VerificationLoop
from family.verification_types import ActionExecution, ActionIntent


@dataclass(slots=True)
class TurnPipelineSeeds:
    previous_handoff: TurnHandoff
    seeded_project: str
    seeded_anchor: str
    seeded_verification: str
    seeded_obligations: list[str]
    disagreement_events: list[dict[str, Any]]
    disagreement_event: DisagreementEvent | None
    disagreement_open: bool


def derive_turn_seeds(
    turn_input: FamilyTurnInput,
    *,
    previous_handoff: TurnHandoff,
    normalized_handoff,
) -> TurnPipelineSeeds:
    seeded_project = turn_input.active_project or previous_handoff.active_project
    seeded_anchor = turn_input.recent_anchor_cue or previous_handoff.continuity_anchor
    seeded_verification = turn_input.verification_status or previous_handoff.verification_status
    seeded_obligations = (
        list(turn_input.open_obligations)
        if turn_input.open_obligations
        else list(previous_handoff.open_obligations)
    )
    disagreement_events = list(turn_input.disagreement_events)
    disagreement_event = primary_disagreement_event(disagreement_events)
    disagreement_open = bool(disagreement_event and disagreement_event.still_open) or normalized_handoff.disagreement_open

    return TurnPipelineSeeds(
        previous_handoff=previous_handoff,
        seeded_project=seeded_project,
        seeded_anchor=seeded_anchor,
        seeded_verification=seeded_verification,
        seeded_obligations=seeded_obligations,
        disagreement_events=disagreement_events,
        disagreement_event=disagreement_event,
        disagreement_open=disagreement_open,
    )


def build_context_view(
    context_builder,
    turn_input: FamilyTurnInput,
    *,
    seeds: TurnPipelineSeeds,
) -> dict[str, Any]:
    context_view = context_builder.build(
        {
            "active_project": seeds.seeded_project,
            "active_mode": seeds.previous_handoff.active_mode,
            "current_task": turn_input.current_task,
            "current_environment_state": turn_input.current_environment_state or "dry family turn pipeline",
            "last_verified_result": turn_input.last_verified_result,
            "open_obligations": seeds.seeded_obligations,
            "verification_status": seeds.seeded_verification,
            "disagreement_events": seeds.disagreement_events,
            "risk_hint": turn_input.monitor_hint,
            "monitor_summary": None,
            "recent_anchor_cue": seeds.seeded_anchor,
        }
    ).to_dict()
    if seeds.disagreement_open and not seeds.disagreement_events and seeds.previous_handoff.shared_disagreement_status != "none":
        context_view["shared_disagreement_status"] = seeds.previous_handoff.shared_disagreement_status
        notes = list(context_view.get("notes", []))
        notes.append("shared disagreement posture carried forward from previous handoff")
        context_view["notes"] = notes
    return context_view


def build_mode_result(
    mode_inference,
    turn_input: FamilyTurnInput,
    *,
    seeds: TurnPipelineSeeds,
    context_view: dict[str, Any],
) -> dict[str, Any]:
    return mode_inference.infer(
        {
            "current_message": turn_input.current_message,
            "active_project": seeds.seeded_project,
            "current_task": turn_input.current_task,
            "recent_anchor_cue": seeds.seeded_anchor,
            "context_view_summary": context_summary(context_view),
            "action_required": turn_input.action_required,
            "disagreement_open": seeds.disagreement_open,
            "verification_status": seeds.seeded_verification,
            "explicit_mode_hint": turn_input.explicit_mode_hint or seeds.previous_handoff.active_mode,
        }
    ).to_dict()


def build_live_state(
    live_state_builder,
    *,
    context_view: dict[str, Any],
    mode_result: dict[str, Any],
    seeds: TurnPipelineSeeds,
    monitor_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    return live_state_builder.build(
        {
            "context_view": context_view,
            "mode_inference_result": mode_result,
            "verification_status": seeds.seeded_verification,
            "active_project": seeds.seeded_project,
            "recent_anchor_cue": seeds.seeded_anchor,
            "disagreement_open": seeds.disagreement_open,
            "monitor_summary": monitor_summary,
            "current_axis_hint": seeds.previous_handoff.current_axis,
        }
    ).to_dict()


def build_monitor_output(
    monitor_layer,
    turn_input: FamilyTurnInput,
    *,
    context_view: dict[str, Any],
    live_state: dict[str, Any],
    mode_result: dict[str, Any],
) -> dict[str, Any]:
    return monitor_layer.pre_action_monitor(
        active_mode=mode_result["active_mode"],
        task_type=task_type(turn_input.current_message, turn_input.current_task),
        context_view={
            "task_focus": context_view["task_focus"],
            "current_execution_boundary": turn_input.execution_intent or turn_input.current_task,
            "continuity_anchor": live_state["continuity_anchor"],
        },
        draft_response=turn_input.current_message,
        archive_status={
            "archive_consulted": turn_input.archive_consulted,
            "fragments_used": 1 if turn_input.archive_consulted else 0,
        },
        project_relevance_markers={
            "project_relevant": project_relevant(turn_input.current_message, turn_input.active_project),
        },
    ).to_dict()


def build_effort_input(
    turn_input: FamilyTurnInput,
    *,
    mode_result: dict[str, Any],
    seeds: TurnPipelineSeeds,
    mirror_summary: dict[str, Any],
) -> EffortInput:
    return EffortInput(
        task_type=task_type(turn_input.current_message, turn_input.current_task),
        domain=domain(seeds.seeded_project, mode_result["active_mode"]),
        active_mode=mode_result["active_mode"],
        mode_confidence=float(mode_result["confidence"]),
        ambiguity_score=ambiguity_score(turn_input.current_message, seeds.disagreement_open, mirror_summary),
        risk_score=risk_score(seeds.seeded_verification, seeds.disagreement_open, mirror_summary),
        stakes_signal=None,
        stakes_confidence=0.0,
        action_required=turn_input.action_required,
        memory_commit_possible=False,
        disagreement_likelihood=0.75 if seeds.disagreement_open else 0.10,
        cue_strength=cue_strength(turn_input.current_message, seeds.seeded_anchor, seeds.seeded_project),
        verification_gap_estimate=0.75 if seeds.seeded_verification.lower() in {"pending", "failed", "unknown"} else 0.10,
        high_risk_domain=False,
        unanswerable_likelihood=0.65 if "not sure" in turn_input.current_message.lower() else 0.10,
    )


def build_execution_request(
    turn_input: FamilyTurnInput,
    *,
    active_project: str,
    classifier: ExecutionRequestClassifier,
) -> ExecutionRequest:
    haystack = f"{turn_input.current_message} {turn_input.current_task} {turn_input.execution_intent}".lower()
    reason = turn_input.execution_intent or turn_input.current_task or turn_input.current_message
    base_payload: dict[str, Any]

    if any(token in haystack for token in ("secret", "token", "credential", "key")):
        base_payload = {
            "action_type": "secret_access",
            "target_type": "secret_ref",
            "target_path_or_ref": reason,
            "requested_zone": "host",
            "writes_state": False,
            "executes_code": False,
            "network_required": False,
            "package_install_required": False,
            "secret_access_required": True,
            "source_trust_stage": "unknown",
            "reason": reason,
        }
    elif any(token in haystack for token in ("http", "https", "download", "fetch", "url", "network", "remote")):
        base_payload = {
            "action_type": "network_access",
            "target_type": "remote_ref",
            "target_path_or_ref": reason,
            "requested_zone": "host",
            "writes_state": False,
            "executes_code": False,
            "network_required": True,
            "package_install_required": False,
            "secret_access_required": False,
            "source_trust_stage": "unknown",
            "reason": reason,
        }
    elif any(token in haystack for token in ("inspect", "read", "list", "metadata")):
        base_payload = {
            "action_type": "inspect",
            "target_type": "repo_metadata",
            "target_path_or_ref": active_project or turn_input.current_task,
            "requested_zone": "inspection",
            "writes_state": False,
            "executes_code": False,
            "network_required": False,
            "package_install_required": False,
            "secret_access_required": False,
            "source_trust_stage": "reviewed",
            "reason": reason,
        }
    elif any(token in haystack for token in ("parse", "analyze", "decode", "transform", "json", "csv", "payload")):
        base_payload = {
            "action_type": "parse_payload",
            "target_type": "structured_payload",
            "target_path_or_ref": reason,
            "requested_zone": "sandbox",
            "writes_state": False,
            "executes_code": False,
            "network_required": False,
            "package_install_required": False,
            "secret_access_required": False,
            "source_trust_stage": "unknown",
            "reason": reason,
        }
    elif any(token in haystack for token in ("install", "package", "dependency", "pip", "pytest")):
        base_payload = {
            "action_type": "install",
            "target_type": "package",
            "target_path_or_ref": reason,
            "requested_zone": "host",
            "writes_state": False,
            "executes_code": False,
            "network_required": False,
            "package_install_required": True,
            "secret_access_required": False,
            "source_trust_stage": "unknown",
            "reason": reason,
        }
    elif any(token in haystack for token in ("propose", "draft patch", "suggest patch")):
        base_payload = {
            "action_type": "propose_patch",
            "target_type": "repo_file",
            "target_path_or_ref": reason,
            "requested_zone": "sandbox",
            "writes_state": True,
            "executes_code": False,
            "network_required": False,
            "package_install_required": False,
            "secret_access_required": False,
            "source_trust_stage": "reviewed",
            "reason": reason,
        }
    elif any(token in haystack for token in ("write", "patch", "apply", "update", "commit", "modify")):
        base_payload = {
            "action_type": "write_file",
            "target_type": "repo_file",
            "target_path_or_ref": reason or active_project,
            "requested_zone": "host",
            "writes_state": True,
            "executes_code": False,
            "network_required": False,
            "package_install_required": False,
            "secret_access_required": False,
            "source_trust_stage": "reviewed",
            "reason": reason,
        }
    else:
        base_payload = {
            "action_type": "shell_execute",
            "target_type": "command",
            "target_path_or_ref": reason,
            "requested_zone": "host",
            "writes_state": False,
            "executes_code": True,
            "network_required": False,
            "package_install_required": False,
            "secret_access_required": False,
            "source_trust_stage": "unknown",
            "reason": reason,
        }

    request = ExecutionRequest(**base_payload)
    classified = classifier.classify(request)
    enriched_request = request.to_dict()
    enriched_request.update(
        {
            "requested_operation": classified.requested_operation,
            "target_scope": classified.target_scope,
            "mutation_depth": classified.mutation_depth,
            "zone_preference": classified.zone_preference,
            "why_not_host_if_applicable": classified.why_not_host_if_applicable,
        }
    )
    return ExecutionRequest(**enriched_request)


def build_verification_record(
    verification_loop: VerificationLoop,
    turn_input: FamilyTurnInput,
    *,
    execution_decision: dict[str, Any],
    seeded_verification: str,
) -> dict[str, Any]:
    notes = ["dry pipeline canary: no real action executed, so verification is conservative"]
    if seeded_verification:
        notes.append(f"incoming verification posture: {seeded_verification}")
    if turn_input.last_verified_result:
        notes.append("last verified result is carried as compact context, not fresh verification")
    if execution_decision:
        notes.append(f"execution gate decision: {execution_decision['decision']}")
        if execution_decision["decision"] == "require_approval":
            notes.append("approval is required before any runtime action can occur")
        elif execution_decision["decision"] == "deny":
            notes.append("runtime action is denied, so no execution outcome exists")
        elif execution_decision["decision"] == "allow":
            notes.append("runtime posture is allowed, but the dry canary still did not execute the action")
    action_intent = ActionIntent(
        intended_action=turn_input.current_task or turn_input.current_message[:80],
        expected_change=turn_input.execution_intent or turn_input.current_task or "dry-run family turn progression",
        notes=[],
    )
    action_execution = ActionExecution(
        executed_action="",
        evidence=[],
        notes=[],
        authoritative_evidence_present=bool(
            turn_input.observed_outcome.observed_outcome.strip()
            and turn_input.observed_outcome.evidence_authority == "authoritative"
        ),
    )
    return verification_loop.post_action_review(
        action_intent,
        action_execution,
        observed_outcome=turn_input.observed_outcome,
        notes=notes,
        expected_change_observable=True,
    ).to_dict()


def build_notes(
    *,
    execution_decision: dict[str, Any],
    verification_record: dict[str, Any],
    disagreement_open: bool,
    normalized_handoff,
    disagreement_event: DisagreementEvent | None,
) -> list[str]:
    notes = ["dry pipeline canary composed family-layer stages without real execution"]
    if execution_decision:
        notes.append(
            f"execution gate result: {execution_decision['decision']} ({execution_decision['recommended_zone']})"
        )
        if execution_decision["decision"] == "require_approval":
            notes.append("runtime action remained approval-gated and was not executed")
        elif execution_decision["decision"] == "deny":
            notes.append("runtime action was denied, so verification remained non-passing")
        else:
            notes.append("execution posture was allowed in principle, but this dry canary still executed nothing")
    else:
        notes.append("no runtime action was requested, so execution objects remained empty")
    if verification_record["verification_status"] == "passed":
        notes.append("verification is evidence-backed by explicit observed outcome")
    elif verification_record["verification_status"] == "failed":
        notes.append("verification is evidence-backed and indicates expected change did not land")
    else:
        notes.append("verification remains conservative unless explicit observed evidence is strong enough")
    if disagreement_open:
        notes.append("open disagreement remained visible across context, live state, router, and compression")
    if verification_record["verification_status"] == "unknown":
        notes.append("verification posture remained visible and was not auto-passed")
    if any(normalized_handoff.handoff.to_dict().values()):
        notes.append("previous handoff supplied compact continuity baton for this turn")
        if normalized_handoff.disagreement_open and disagreement_event is None:
            notes.append("handoff carried open disagreement status without reconstructing a synthetic event")
    return notes


def context_summary(context_view: dict[str, Any]) -> str:
    return " ".join(
        [
            str(context_view.get("task_focus", "")),
            str(context_view.get("current_risk", "")),
            str(context_view.get("shared_disagreement_status", "")),
        ]
    ).strip()


def task_type(message: str, current_task: str) -> str:
    haystack = f"{message} {current_task}".lower()
    if any(token in haystack for token in ("review", "debug", "correctness", "audit", "verify")):
        return "verify"
    if any(token in haystack for token in ("architecture", "build", "implementation", "code", "scaffold")):
        return "architecture"
    if any(token in haystack for token in ("research", "investigate")):
        return "research"
    if any(token in haystack for token in ("run", "apply", "perform", "update", "execute")):
        return "execution"
    return "chat"


def domain(active_project: str, active_mode: str) -> str:
    if active_project:
        return "build"
    if active_mode in {"care", "playful"}:
        return "relational"
    if active_mode == "audit":
        return "audit"
    return "generic"


def ambiguity_score(message: str, disagreement_open: bool, mirror_summary: dict[str, Any]) -> float:
    haystack = message.lower()
    if mirror_summary.get("primary_risk") == "ambiguity":
        return 0.80
    if disagreement_open or any(token in haystack for token in ("not sure", "either", "both", "ambiguous")):
        return 0.75
    return 0.20


def risk_score(verification_status: str, disagreement_open: bool, mirror_summary: dict[str, Any]) -> float:
    if verification_status.lower() in {"pending", "failed", "unknown"}:
        return 0.80
    if disagreement_open:
        return 0.65
    if mirror_summary.get("primary_risk") in {"fake_progress", "mode_decay"}:
        return 0.70
    return 0.20


def cue_strength(message: str, recent_anchor_cue: str, active_project: str) -> float:
    haystack = message.lower()
    supports = 0
    for cue in (recent_anchor_cue, active_project):
        tokens = [token for token in re.findall(r"[a-z0-9_]+", cue.lower()) if len(token) >= 3]
        if cue and any(token in haystack for token in tokens):
            supports += 1
    if supports >= 2:
        return 0.85
    if supports == 1:
        return 0.55
    return 0.10


def project_relevant(message: str, active_project: str) -> bool:
    if not active_project:
        return True
    return active_project.lower() in message.lower()


def primary_disagreement_event(disagreement_events: list[dict[str, Any]]) -> DisagreementEvent | None:
    for event in disagreement_events:
        if event.get("still_open", False):
            return DisagreementEvent(
                event_id=str(event.get("event_id", "dg_pipeline")),
                timestamp=str(event.get("timestamp", "2026-04-17T00:00:00Z")),
                disagreement_type=str(event.get("disagreement_type", "action")),
                tracey_position=str(event.get("tracey_position", "preserve local continuity line")),
                seyn_position=str(event.get("seyn_position", "preserve verification-first line")),
                severity=float(event.get("severity", 0.70)),
                still_open=bool(event.get("still_open", True)),
                later_resolution=str(event.get("later_resolution", "")),
                house_law_implicated=str(event.get("house_law_implicated", "")),
                action_lead_selected=event.get("action_lead_selected"),
                epistemic_resolution_claimed=bool(event.get("epistemic_resolution_claimed", False)),
            )
    return None


def default_previous_live_state(
    turn_input: FamilyTurnInput,
    *,
    context_view: dict[str, Any],
    mode_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "active_mode": mode_result["active_mode"],
        "current_axis": context_view["task_focus"] or "maintain current state",
        "coherence_level": "mixed" if turn_input.verification_status.lower() in {"pending", "failed", "unknown"} else "stable",
        "tension_flags": [],
        "policy_pressure": "low",
        "active_project": turn_input.active_project,
        "continuity_anchor": turn_input.recent_anchor_cue or turn_input.active_project,
        "user_signal": context_view["task_focus"],
        "archive_needed": False,
        "verification_status": "passed" if turn_input.last_verified_result and not turn_input.verification_status else turn_input.verification_status,
    }


def detected_cues(message: str, recent_anchor_cue: str, active_project: str) -> list[str]:
    cues = []
    for cue in (recent_anchor_cue, active_project):
        if cue:
            cues.append(cue)
    cues.extend(token for token in re.findall(r"[a-z0-9_]+", message.lower()) if len(token) >= 5)
    compact: list[str] = []
    for cue in cues:
        if cue not in compact:
            compact.append(cue)
    return compact[:5]
