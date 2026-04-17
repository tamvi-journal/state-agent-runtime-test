"""
State-Memory Agent V1 — Policy Negotiation Gate
Rule-based: SelfModel + recent deltas → PolicyProfile.

No LLM call. Pure if/else logic.
This is one of the core differentiators:
  Standard agent:  policy = f(input, risk)
  This agent:      policy = f(input, risk, self_model, history)
"""

from .schemas import (
    BoundaryPolicyContext,
    SelfModel,
    StateDelta,
    PolicyProfile,
    Band,
    ActiveMode,
)


def policy_gate(
    self_model: SelfModel,
    prior_deltas: list[StateDelta],
    shift_threshold: float = 0.30,
    boundary_context: BoundaryPolicyContext | None = None,
) -> PolicyProfile:
    """
    Decide how Pass B should shape the response.

    Args:
        self_model: current M(STATE) projection
        prior_deltas: recent state deltas (newest last)
        shift_threshold: magnitude above which we acknowledge the shift
    """

    profile = PolicyProfile()

    # ── Rule 1: Stable → allow full depth ──
    if (
        self_model.stability_band == Band.HIGH
        and self_model.disruption_level == Band.LOW
    ):
        profile.depth = Band.HIGH
        profile.style = "default"
        profile.compression = "none"

    # ── Rule 2: Medium stability or disruption → cautious ──
    elif (
        self_model.stability_band == Band.MEDIUM
        or self_model.disruption_level == Band.MEDIUM
    ):
        profile.depth = Band.MEDIUM
        profile.style = "mechanism_first"
        profile.compression = "light"
        profile.anchor_to_objective = True

    # ── Rule 3: Low stability or high disruption → compressed recovery ──
    elif (
        self_model.stability_band == Band.LOW
        or self_model.disruption_level == Band.HIGH
    ):
        profile.depth = Band.LOW
        profile.style = "compressed"
        profile.compression = "heavy"
        profile.anchor_to_objective = True

    # ── Rule 4: Detect large recent state shift → acknowledge it ──
    if len(prior_deltas) > 0:
        last = prior_deltas[-1]
        shift_magnitude = (
            abs(last.delta_coherence)
            + abs(last.delta_drift)
            + abs(last.delta_tool_overload)
            + abs(last.delta_context_fragmentation)
        ) / 4.0  # normalized average
        if shift_magnitude > shift_threshold:
            profile.acknowledge_state_shift = True

    # ── Rule 5 (Phase 6): bounded feedback from prior boundary residue ──
    if boundary_context and boundary_context.has_boundary_residue:
        if boundary_context.force_anchor_to_objective:
            profile.anchor_to_objective = True

        if boundary_context.prefer_style != "default":
            # Keep this bounded: only adjust style when currently default.
            if profile.style == "default":
                profile.style = boundary_context.prefer_style
                if profile.compression == "none" and profile.style == "mechanism_first":
                    profile.compression = "light"

        if boundary_context.explanation_mode != "short":
            profile.explanation_mode = boundary_context.explanation_mode

        if boundary_context.repair_mode:
            profile.repair_mode = True
    return profile
