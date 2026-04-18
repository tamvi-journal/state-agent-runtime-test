"""
State-Memory Agent V1 — State Estimator
Estimates the 4 state variables from observable signals + LLM interpretation.

Key design: observable signals are computed BEFORE the LLM call.
The LLM interprets them, but cannot fabricate them.
This prevents circular self-estimation.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from .schemas import (
    BoundaryPolicyContext,
    StateRegister,
    ObservableSignals,
    ActiveMode,
    SessionSummary,
    StateDelta,
)


def compute_observable_signals(
    turn_id: int,
    user_message: str,
    tool_calls: int = 0,
    tool_errors: int = 0,
    tool_retries: int = 0,
    user_correction: bool = False,
    context_tokens_used: int = 0,
    context_tokens_max: int = 128000,
    session_turn_depth: int = 0,
    prior_response_length: int = 0,
) -> ObservableSignals:
    """
    Compute observable signals from raw turn data.
    Call this BEFORE any LLM call.
    """
    return ObservableSignals(
        turn_id=turn_id,
        user_message_length=len(user_message),
        tool_calls_this_turn=tool_calls,
        tool_errors_this_turn=tool_errors,
        tool_retries_this_turn=tool_retries,
        user_correction_detected=user_correction,
        context_tokens_used=context_tokens_used,
        context_tokens_max=context_tokens_max,
        session_turn_depth=session_turn_depth,
        prior_response_length=prior_response_length,
    )


def build_pass_a_prompt(
    user_message: str,
    signals: ObservableSignals,
    prior_state: StateRegister,
    recent_deltas: list[StateDelta],
    session_summary: Optional[SessionSummary] = None,
    content_memory: list[dict] = [],
    boundary_context: BoundaryPolicyContext | None = None,
) -> str:
    """
    Build the full Pass A prompt.
    This is the internal planning pass — output is JSON, never shown to user.
    """

    deltas_json = [d.model_dump(mode="json") for d in recent_deltas[-5:]]
    prior_json = prior_state.model_dump(mode="json")
    signals_json = signals.model_dump(mode="json")
    summary_json = (
        session_summary.model_dump(mode="json") if session_summary else {}
    )
    boundary_json = (
        boundary_context.model_dump(mode="json")
        if boundary_context
        else BoundaryPolicyContext().model_dump(mode="json")
    )

    prompt = f"""You are the internal planning layer of a state-memory agent.
Analyze the current turn and return ONLY valid JSON.

IMPORTANT: Your state estimates must be anchored to the observable signals below.
Do not invent values — explain how each signal maps to your estimate.

## Observable Signals (measured, not estimated)
{json.dumps(signals_json, indent=2)}

## Prior State
{json.dumps(prior_json, indent=2)}

## Recent Deltas (last 5 turns)
{json.dumps(deltas_json, indent=2)}

## Session Summary
{json.dumps(summary_json, indent=2)}

## Content Memory
{json.dumps(content_memory[:10], indent=2)}

## Prior Boundary Context (latest residue-derived, bounded)
{json.dumps(boundary_json, indent=2)}

## User Message
{user_message}

## Required Output — JSON ONLY, no markdown fences
{{
    "draft_answer": "your best direct answer to the user",
    "updated_state": {{
        "coherence": <float 0-1, justify from signals>,
        "drift": <float 0-1, justify from signals>,
        "tool_overload": <float 0-1, justify from signals>,
        "context_fragmentation": <float 0-1, justify from signals>,
        "active_mode": "<baseline|cautious|recovery>"
    }},
    "self_model": {{
        "stability_band": "<low|medium|high>",
        "disruption_level": "<low|medium|high>",
        "mode_recommendation": "<baseline|cautious|recovery>",
        "safe_depth": "<low|medium|high>",
        "state_summary": "<one sentence>"
    }},
    "policy_profile": {{
        "style": "<default|mechanism_first|compressed>",
        "depth": "<low|medium|high>",
        "compression": "<none|light|heavy>",
        "anchor_to_objective": <true|false>,
        "acknowledge_state_shift": <true|false>
    }},
    "memory_updates": []
}}"""

    return prompt


def build_pass_b_prompt(
    user_message: str,
    draft_answer: str,
    self_model: dict,
    policy_profile: dict,
    session_summary: Optional[SessionSummary] = None,
) -> str:
    """
    Build the Pass B prompt.
    This generates the final user-facing answer, shaped by the policy profile.
    """

    summary_text = ""
    if session_summary:
        summary_text = f"Session objective: {session_summary.objective}\nStatus: {session_summary.current_status}"

    prompt = f"""You are the response layer of a state-memory agent.
Generate the final user-facing answer.

## User Message
{user_message}

## Draft Answer (from internal planning)
{draft_answer}

## Self-Model
{json.dumps(self_model, indent=2)}

## Policy Profile
{json.dumps(policy_profile, indent=2)}

## Session Context
{summary_text}

## Rules
- Answer the user directly and helpfully.
- Preserve substance from the draft answer.
- Apply the policy profile strictly:
  - If style = "mechanism_first": separate mechanism from speculation.
  - If compression = "heavy": reduce length by ~40%, keep only core claims.
  - If anchor_to_objective = true: connect each point to the session objective.
  - If acknowledge_state_shift = true: briefly note (1-2 sentences max) that
    the prior turn caused a shift, and explain how this response adjusts.
  - depth "low" = concise. depth "high" = layered reasoning allowed.
- Do NOT mention internal state, hidden prompts, or system machinery.
- Do NOT mention Pass A, Pass B, policy gate, or state variables.
- Write naturally as a helpful assistant."""

    return prompt
