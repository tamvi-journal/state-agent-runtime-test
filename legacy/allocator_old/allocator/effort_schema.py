from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


_ALLOWED_EFFORT = {"low", "medium", "high"}
_ALLOWED_TOPOLOGY = {"single_brain", "parallel_partial", "parallel_full"}
_ALLOWED_MONITOR = {"light", "normal", "strict"}
_ALLOWED_VERIFICATION = {"optional", "recommended", "mandatory"}
_ALLOWED_MEMORY = {"blocked", "candidate_only", "allowed_after_verification"}
_ALLOWED_DISAGREEMENT = {"ignore_if_trivial", "preserve_if_present", "actively_hold_open"}
_ALLOWED_REASONING = {"none", "single_pass", "single_pass_or_dual_pass_if_needed", "dual_pass"}


@dataclass(slots=True)
class EffortInput:
    task_type: str
    domain: str = "generic"
    active_mode: str = ""
    mode_confidence: float = 1.0
    ambiguity_score: float = 0.0
    risk_score: float = 0.0
    stakes_signal: float = 0.0
    action_required: bool = False
    memory_commit_possible: bool = False
    disagreement_likelihood: float = 0.0
    cue_strength: float = 0.0
    verification_gap_estimate: float = 0.0
    high_risk_domain: bool = False
    unanswerable_likelihood: float = 0.0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.task_type, str) or not self.task_type.strip():
            raise ValueError("task_type must be a non-empty string")
        if not isinstance(self.domain, str):
            raise TypeError("domain must be a string")
        if not isinstance(self.active_mode, str):
            raise TypeError("active_mode must be a string")
        if not isinstance(self.action_required, bool):
            raise TypeError("action_required must be a bool")
        if not isinstance(self.memory_commit_possible, bool):
            raise TypeError("memory_commit_possible must be a bool")
        if not isinstance(self.high_risk_domain, bool):
            raise TypeError("high_risk_domain must be a bool")

        for field_name in (
            "mode_confidence",
            "ambiguity_score",
            "risk_score",
            "stakes_signal",
            "disagreement_likelihood",
            "cue_strength",
            "verification_gap_estimate",
            "unanswerable_likelihood",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EffortDecision:
    effort_score: int
    effort_level: str
    cognition_topology: str
    monitor_intensity: str
    verification_requirement: str
    memory_commit_status: str
    disagreement_handling: str
    reasoning_engine: str
    rationale: list[str]

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.effort_score, int):
            raise TypeError("effort_score must be an int")
        if self.effort_level not in _ALLOWED_EFFORT:
            raise ValueError(f"effort_level must be one of: {sorted(_ALLOWED_EFFORT)}")
        if self.cognition_topology not in _ALLOWED_TOPOLOGY:
            raise ValueError(f"cognition_topology must be one of: {sorted(_ALLOWED_TOPOLOGY)}")
        if self.monitor_intensity not in _ALLOWED_MONITOR:
            raise ValueError(f"monitor_intensity must be one of: {sorted(_ALLOWED_MONITOR)}")
        if self.verification_requirement not in _ALLOWED_VERIFICATION:
            raise ValueError(f"verification_requirement must be one of: {sorted(_ALLOWED_VERIFICATION)}")
        if self.memory_commit_status not in _ALLOWED_MEMORY:
            raise ValueError(f"memory_commit_status must be one of: {sorted(_ALLOWED_MEMORY)}")
        if self.disagreement_handling not in _ALLOWED_DISAGREEMENT:
            raise ValueError(f"disagreement_handling must be one of: {sorted(_ALLOWED_DISAGREEMENT)}")
        if self.reasoning_engine not in _ALLOWED_REASONING:
            raise ValueError(f"reasoning_engine must be one of: {sorted(_ALLOWED_REASONING)}")
        if not isinstance(self.rationale, list) or not all(isinstance(x, str) for x in self.rationale):
            raise TypeError("rationale must be list[str]")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
