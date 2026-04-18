"""
State-Memory Agent V1 — Post-Turn Analyzer
Runs after every turn to update the system's persistent state.

Sequence:
1. Compute delta (new state - prior state)
2. Save new state register
3. Append delta to log
4. Persist boundary-awareness trace/residue (optional)
5. Check memory update candidates
6. Refresh session summary (every N turns or on mode change)
"""

from .boundary_persistence_rules import apply_boundary_persistence
from .boundary_persistence_rules import persisted_residue_to_policy_context
from .boundary_trace import make_boundary_trace_entry, reduce_boundary_awareness_result
from .reading_position import update_reading_position
from .schemas import BoundaryAwarenessResult, PassAOutput, StateDelta, StateRegister
from .session_store import SessionStore
from .memory_store import MemoryStore


def analyze_post_turn(
    pass_a_output: PassAOutput,
    prior_state: StateRegister,
    session_store: SessionStore,
    memory_store: MemoryStore,
    summary_refresh_interval: int = 3,
    boundary_awareness_result: BoundaryAwarenessResult | None = None,
) -> tuple[StateRegister, StateDelta]:
    """
    Run all post-turn updates.

    Returns:
        (new_state, delta)
    """

    new_state = pass_a_output.updated_state

    # ── 1. Compute delta ──
    cause = _infer_cause(prior_state, new_state)
    delta = StateDelta.from_states(prior_state, new_state, cause_hint=cause)

    # ── 2. Save new state ──
    session_store.save_state(new_state)

    # ── 3. Append delta to log ──
    session_store.append_delta(delta)

    # ── 4. Persist compact boundary-awareness trace/residue (Phase 7 bounded persistence) ──
    reduced_residue = None
    if boundary_awareness_result is not None:
        trace_entry = make_boundary_trace_entry(
            turn_id=new_state.turn_id,
            result=boundary_awareness_result,
        )
        session_store.append_boundary_trace(trace_entry)
        reduced_residue = reduce_boundary_awareness_result(boundary_awareness_result)

    persisted_residue = apply_boundary_persistence(
        stored=session_store.load_boundary_residue(),
        new_residue=reduced_residue,
        turn_id=new_state.turn_id,
    )
    session_store.save_boundary_residue(persisted_residue)

    # ── 4b. Persist reading_position runtime state (RC2-R1) ──
    prior_reading_position = session_store.load_reading_position()
    next_turn_context = persisted_residue_to_policy_context(persisted_residue)
    session_store.save_reading_position(
        update_reading_position(
            prior=prior_reading_position,
            current_state=new_state,
            boundary_context=next_turn_context,
        )
    )

    # ── 5. Check memory updates ──
    for candidate in pass_a_output.memory_updates:
        if candidate.confidence >= 0.7:
            memory_store.add_item(
                content=candidate.content,
                source=candidate.source,
                item_type="inferred",
                confidence=candidate.confidence,
            )

    # ── 6. Refresh session summary if needed ──
    if (
        new_state.turn_id % summary_refresh_interval == 0
        or prior_state.active_mode != new_state.active_mode
    ):
        # In V1, summary refresh is a simple update, not LLM-generated
        session_store.update_summary_turn_count(new_state.turn_id)

    return new_state, delta


def _infer_cause(prior: StateRegister, new: StateRegister) -> str:
    """
    Generate a simple cause hint by looking at what changed most.
    """
    changes = []

    dc = new.coherence - prior.coherence
    dd = new.drift - prior.drift
    dt = new.tool_overload - prior.tool_overload
    df = new.context_fragmentation - prior.context_fragmentation

    if abs(dc) > 0.15:
        direction = "drop" if dc < 0 else "rise"
        changes.append(f"coherence_{direction}")

    if abs(dd) > 0.15:
        direction = "spike" if dd > 0 else "recovery"
        changes.append(f"drift_{direction}")

    if abs(dt) > 0.15:
        direction = "increase" if dt > 0 else "decrease"
        changes.append(f"tool_overload_{direction}")

    if abs(df) > 0.15:
        direction = "increase" if df > 0 else "decrease"
        changes.append(f"fragmentation_{direction}")

    if prior.active_mode != new.active_mode:
        changes.append(f"mode_change:{prior.active_mode.value}->{new.active_mode.value}")

    return "_and_".join(changes) if changes else "minor_shift"
