"""
State-Memory Agent V1 — Self-Model Projection
Projects raw StateRegister floats into categorical SelfModel bands.

Pure function. No LLM call. No side effects.
M(STATE) → compact object the policy gate can read.
"""

from .schemas import StateRegister, SelfModel, Band, ActiveMode


def project_self_model(state: StateRegister) -> SelfModel:
    """
    Project raw state floats into categorical bands.

    stability  = coherence adjusted by drift (higher = more stable)
    disruption = average of tool_overload + context_fragmentation
    """

    # ── Stability: coherence discounted by drift ──
    stability_score = state.coherence * (1.0 - state.drift)
    if stability_score > 0.65:
        stability_band = Band.HIGH
    elif stability_score > 0.35:
        stability_band = Band.MEDIUM
    else:
        stability_band = Band.LOW

    # ── Disruption: tool problems + context scatter ──
    disruption_score = (state.tool_overload + state.context_fragmentation) / 2.0
    if disruption_score > 0.55:
        disruption_level = Band.HIGH
    elif disruption_score > 0.30:
        disruption_level = Band.MEDIUM
    else:
        disruption_level = Band.LOW

    # ── Mode recommendation ──
    if stability_band == Band.LOW or disruption_level == Band.HIGH:
        mode = ActiveMode.RECOVERY
    elif stability_band == Band.MEDIUM or disruption_level == Band.MEDIUM:
        mode = ActiveMode.CAUTIOUS
    else:
        mode = ActiveMode.BASELINE

    # ── Safe depth ──
    if stability_band == Band.HIGH and disruption_level == Band.LOW:
        safe_depth = Band.HIGH
    elif stability_band == Band.LOW or disruption_level == Band.HIGH:
        safe_depth = Band.LOW
    else:
        safe_depth = Band.MEDIUM

    # ── Human-readable summary ──
    summary = (
        f"Stability {stability_band.value}, "
        f"disruption {disruption_level.value}. "
        f"coherence={state.coherence:.2f}, "
        f"drift={state.drift:.2f}, "
        f"tool_overload={state.tool_overload:.2f}, "
        f"fragmentation={state.context_fragmentation:.2f}."
    )

    return SelfModel(
        stability_band=stability_band,
        disruption_level=disruption_level,
        mode_recommendation=mode,
        safe_depth=safe_depth,
        state_summary=summary,
    )
