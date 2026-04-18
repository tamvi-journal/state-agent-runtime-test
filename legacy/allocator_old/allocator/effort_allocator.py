from __future__ import annotations

from dataclasses import dataclass

from allocator.effort_schema import EffortDecision, EffortInput


@dataclass(slots=True)
class EffortAllocator:
    """
    Heuristic family-level routing valve.

    Phase 2.5 goals:
    - estimate how much cognition this turn deserves
    - route verification posture
    - route memory gating
    - route disagreement posture
    - keep decisions inspectable and stake-aware
    """

    default_unknown_stakes_to_medium: bool = True

    def route(self, effort_input: EffortInput | dict) -> EffortDecision:
        if isinstance(effort_input, dict):
            effort_input = EffortInput(**effort_input)

        score = 0
        rationale: list[str] = []

        if effort_input.task_type in {"architecture", "execution", "research", "verify"}:
            score += 2
            rationale.append("task_type is architecture/execution/research/verify (+2)")

        if effort_input.ambiguity_score >= 0.70:
            score += 2
            rationale.append("ambiguity_score >= 0.70 (+2)")

        if effort_input.risk_score >= 0.70:
            score += 2
            rationale.append("risk_score >= 0.70 (+2)")

        if effort_input.stakes_signal >= 0.70:
            score += 2
            rationale.append("stakes_signal >= 0.70 (+2)")

        if effort_input.action_required:
            score += 2
            rationale.append("action_required is true (+2)")

        if effort_input.memory_commit_possible:
            score += 2
            rationale.append("memory_commit_possible is true (+2)")

        if effort_input.disagreement_likelihood >= 0.60:
            score += 2
            rationale.append("disagreement_likelihood >= 0.60 (+2)")

        if effort_input.mode_confidence < 0.50:
            score += 1
            rationale.append("mode_confidence < 0.50 (+1)")

        if effort_input.verification_gap_estimate >= 0.60:
            score += 1
            rationale.append("verification_gap_estimate >= 0.60 (+1)")

        if effort_input.high_risk_domain:
            score += 2
            rationale.append("high_risk_domain is true (+2)")

        if effort_input.unanswerable_likelihood >= 0.60:
            score += 1
            rationale.append("unanswerable_likelihood >= 0.60 (+1)")

        if effort_input.cue_strength >= 0.75:
            score -= 2
            rationale.append("cue_strength >= 0.75 (-2)")

        if effort_input.task_type in {"rewrite", "formatting", "small_talk"}:
            score -= 2
            rationale.append("task_type is rewrite/formatting/small_talk (-2)")

        effort_level = self._effort_level_from_score(score)

        # v0.1.2 note: if stakes are unclear, default medium instead of low
        if (
            self.default_unknown_stakes_to_medium
            and effort_level == "low"
            and effort_input.stakes_signal == 0.0
        ):
            effort_level = "medium"
            rationale.append("stakes unclear -> precautionary default medium")

        cognition_topology = self._topology(effort_level)
        monitor_intensity = self._monitor_intensity(effort_level)
        verification_requirement = self._verification_requirement(effort_level, effort_input)
        memory_commit_status = self._memory_status(effort_level, effort_input)
        disagreement_handling = self._disagreement_handling(effort_level)
        reasoning_engine = self._reasoning_engine(effort_level, effort_input)

        return EffortDecision(
            effort_score=score,
            effort_level=effort_level,
            cognition_topology=cognition_topology,
            monitor_intensity=monitor_intensity,
            verification_requirement=verification_requirement,
            memory_commit_status=memory_commit_status,
            disagreement_handling=disagreement_handling,
            reasoning_engine=reasoning_engine,
            rationale=rationale,
        )

    @staticmethod
    def _effort_level_from_score(score: int) -> str:
        if score <= 1:
            return "low"
        if 2 <= score <= 5:
            return "medium"
        return "high"

    @staticmethod
    def _topology(effort_level: str) -> str:
        if effort_level == "low":
            return "single_brain"
        if effort_level == "medium":
            return "parallel_partial"
        return "parallel_full"

    @staticmethod
    def _monitor_intensity(effort_level: str) -> str:
        if effort_level == "low":
            return "light"
        if effort_level == "medium":
            return "normal"
        return "strict"

    @staticmethod
    def _verification_requirement(effort_level: str, effort_input: EffortInput) -> str:
        if effort_input.action_required or effort_input.high_risk_domain:
            return "mandatory"
        if effort_level == "low":
            return "optional"
        return "recommended"

    @staticmethod
    def _memory_status(effort_level: str, effort_input: EffortInput) -> str:
        if effort_input.memory_commit_possible and effort_level == "high":
            return "allowed_after_verification"
        if effort_level == "medium":
            return "candidate_only"
        return "blocked"

    @staticmethod
    def _disagreement_handling(effort_level: str) -> str:
        if effort_level == "low":
            return "ignore_if_trivial"
        if effort_level == "medium":
            return "preserve_if_present"
        return "actively_hold_open"

    @staticmethod
    def _reasoning_engine(effort_level: str, effort_input: EffortInput) -> str:
        if effort_level == "low":
            return "single_pass"
        if effort_level == "medium":
            if (
                effort_input.ambiguity_score >= 0.70
                or effort_input.disagreement_likelihood >= 0.60
                or effort_input.unanswerable_likelihood >= 0.60
            ):
                return "single_pass_or_dual_pass_if_needed"
            return "single_pass"
        return "dual_pass"
