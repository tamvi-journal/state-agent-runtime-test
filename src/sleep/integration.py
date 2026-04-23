from __future__ import annotations

from typing import Any

from sleep.contracts import build_default_sleep_patch


def apply_wake_result_to_runtime_state(
    runtime_state: dict[str, Any],
    wake_result: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(runtime_state or {})
    patch = build_default_sleep_patch()
    constraints = dict(wake_result.get("constraints", {}))
    resume_class = str(wake_result.get("resume_class", "none"))
    patch.update(
        {
            "sleep_state": {
                "full_resume": "resumed",
                "degraded_resume": "degraded_resume",
                "clarify_first": "clarify_first",
                "blocked": "blocked",
            }.get(resume_class, "wake_sanity"),
            "resume_class": resume_class,
            "wake_constraints_active": resume_class != "full_resume",
            "wake_requires_revalidation": list(constraints.get("requires_revalidation", [])),
            "wake_forbidden_claims": list(constraints.get("forbidden_claims", [])),
            "wake_summary": str(wake_result.get("summary", "")),
        }
    )
    updated.update(patch)
    return updated


def build_tracey_wake_hints(wake_result: dict[str, Any]) -> dict[str, Any]:
    constraints = dict(wake_result.get("constraints", {}))
    return {
        "resume_class": str(wake_result.get("resume_class", "none")),
        "wake_constraints_active": str(wake_result.get("resume_class", "none")) != "full_resume",
        "requires_revalidation": list(constraints.get("requires_revalidation", [])),
        "forbidden_claims": list(constraints.get("forbidden_claims", [])),
        "wake_summary": str(wake_result.get("summary", "")),
    }


def rebuild_baton_after_wake(
    post_turn_result: dict[str, Any],
    wake_result: dict[str, Any],
) -> dict[str, Any]:
    baton = dict(post_turn_result.get("handoff_baton", {}))
    if not baton:
        return baton

    resume_class = str(wake_result.get("resume_class", "none"))
    summary = str(wake_result.get("summary", "")).strip()
    if resume_class in {"degraded_resume", "clarify_first", "blocked"}:
        baton["next_hint"] = summary or baton.get("next_hint", "")
        baton["monitor_summary"] = {
            "wake_resume_class": resume_class,
            "wake_summary": summary,
        }
    return baton
