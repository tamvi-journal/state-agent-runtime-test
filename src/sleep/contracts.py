from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SleepState = Literal[
    "active",
    "sleep_prepare",
    "sleeping",
    "wake_restore",
    "wake_sanity",
    "resumed",
    "degraded_resume",
    "clarify_first",
    "blocked",
    "emergency_sleep",
]

ResumeClass = Literal[
    "none",
    "full_resume",
    "degraded_resume",
    "clarify_first",
    "blocked",
]

WakeCheckStatus = Literal["pass", "partial", "fail"]
WakeStatus = Literal["passed", "degraded", "clarify", "blocked"]
SleepLevel = Literal["light", "normal", "hard", "unknown"]

SLEEP_SNAPSHOT_SCHEMA_VERSION = "state-agent-sleep-snapshot/v0.1"
DEFAULT_SLEEP_STATE: SleepState = "active"
DEFAULT_RESUME_CLASS: ResumeClass = "none"

WAKE_CHECK_NAMES: tuple[str, ...] = (
    "identity_continuity",
    "thread_continuity",
    "memory_authority",
    "handle_validity",
    "boundary_match",
    "truth_posture",
)

RESUME_CLASSES_REQUIRING_CONSTRAINTS: tuple[ResumeClass, ...] = (
    "degraded_resume",
    "clarify_first",
    "blocked",
)


@dataclass(slots=True)
class WakeConstraints:
    allow_direct_resume: bool = False
    requires_revalidation: list[str] = field(default_factory=list)
    forbidden_claims: list[str] = field(default_factory=list)
    must_clarify: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "allow_direct_resume": self.allow_direct_resume,
            "requires_revalidation": list(self.requires_revalidation),
            "forbidden_claims": list(self.forbidden_claims),
            "must_clarify": list(self.must_clarify),
        }


@dataclass(slots=True)
class WakeSanityResult:
    status: WakeStatus
    resume_class: ResumeClass
    summary: str
    checks: dict[str, WakeCheckStatus]
    constraints: WakeConstraints = field(default_factory=WakeConstraints)
    risk_notes: list[str] = field(default_factory=list)
    snapshot_candidate: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "resume_class": self.resume_class,
            "summary": self.summary,
            "checks": dict(self.checks),
            "constraints": self.constraints.to_dict(),
            "risk_notes": list(self.risk_notes),
            "snapshot_candidate": self.snapshot_candidate,
        }


def build_default_sleep_patch() -> dict[str, object]:
    return {
        "sleep_state": DEFAULT_SLEEP_STATE,
        "sleep_level": "unknown",
        "resume_class": DEFAULT_RESUME_CLASS,
        "wake_constraints_active": False,
        "wake_requires_revalidation": [],
        "wake_forbidden_claims": [],
        "wake_summary": "",
    }


def normalize_sleep_level(value: str | None) -> SleepLevel:
    lowered = str(value or "unknown").strip().lower()
    if lowered in {"light", "normal", "hard"}:
        return lowered
    return "unknown"
