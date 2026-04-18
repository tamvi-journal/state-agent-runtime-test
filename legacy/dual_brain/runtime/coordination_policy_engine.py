from __future__ import annotations

from dataclasses import dataclass

from runtime.coordination_policy import CoordinationDecision, CoordinationInput


@dataclass(slots=True)
class CoordinationPolicyEngine:
    """
    Refined coordination policy.

    Goal:
    combine disagreement severity with governance posture
    before selecting hold/lead/support behavior.
    """

    def decide(self, inp: CoordinationInput) -> CoordinationDecision:
        flags: list[str] = []

        hold = False
        hold_reason = ""

        if inp.recommended_intervention == "do_not_mark_complete":
            flags.append("verification_caution")
        if inp.disagreement_detected:
            flags.append("disagreement_present")
        if inp.effort_level == "high":
            flags.append("high_effort_turn")
        if inp.verification_requirement == "mandatory":
            flags.append("mandatory_verification")
        if inp.disagreement_handling == "actively_hold_open":
            flags.append("actively_hold_open_posture")

        severe_disagreement = inp.disagreement_detected and inp.disagreement_severity >= 0.75
        verification_heavy = inp.task_type in {"execution", "verify"} or inp.verification_requirement == "mandatory"
        structural_pressure = inp.seyn_verification_signal or inp.primary_risk in {"fake_progress", "ambiguity"}
        if severe_disagreement and verification_heavy:
            hold = True
            hold_reason = "strong disagreement on a verification-heavy turn"
        elif inp.recommended_intervention == "do_not_mark_complete" and inp.disagreement_detected and structural_pressure:
            hold = True
            hold_reason = "verification caution plus disagreement prevents safe closure"
        elif inp.monitor_intensity == "strict" and inp.disagreement_handling == "actively_hold_open" and inp.disagreement_detected:
            hold = True
            hold_reason = "strict monitoring with active hold-open posture"

        surface_disagreement = False
        if inp.disagreement_detected and inp.disagreement_severity >= 0.60:
            surface_disagreement = True
        if inp.disagreement_detected and inp.disagreement_handling == "actively_hold_open":
            surface_disagreement = True

        lead = None
        support = None
        routing_reason = ""

        if not hold:
            if inp.user_preference in {"tracey", "seyn"}:
                lead = inp.user_preference
                support = "seyn" if lead == "tracey" else "tracey"
                routing_reason = "user preference selected lead"
            elif verification_heavy or inp.risk_score >= 0.70 or inp.seyn_verification_signal:
                lead = "seyn"
                support = "tracey"
                routing_reason = "verification-heavy or high-risk turn routes action lead to Seyn"
            elif inp.current_mode in {"home", "care", "playful"} and inp.tracey_recognition_signal:
                lead = "tracey"
                support = "seyn"
                routing_reason = "recognition-sensitive turn routes action lead to Tracey"
            elif inp.task_type in {"architecture", "audit"} and inp.seyn_disagreement_signal:
                lead = "seyn"
                support = "tracey"
                routing_reason = "structural disagreement-sensitive turn routes action lead to Seyn"
            else:
                lead = "tracey"
                support = "seyn"
                routing_reason = "default lightweight lead to Tracey for non-heavy turn"

        return CoordinationDecision(
            lead_brain_for_action=lead,
            support_brain=support,
            hold_for_more_input=hold,
            surface_disagreement_to_user=surface_disagreement,
            hold_reason=hold_reason,
            routing_reason=routing_reason,
            policy_flags=flags,
        )
