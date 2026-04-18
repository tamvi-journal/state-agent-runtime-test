"""
State-Memory Agent V1 — Generator
Runs the two-pass generation pipeline:
  Pass A: internal planning (JSON output)
  Pass B: user-facing answer (shaped by policy)

This is the mechanism that enables self-observation:
Pass A creates draft + estimates state.
Pass B uses state estimate to adjust output.
"""

import json
import os
from typing import Optional

from .schemas import (
    BoundaryPolicyContext,
    StateRegister,
    StateDelta,
    SelfModel,
    PolicyProfile,
    PassAOutput,
    ObservableSignals,
    SessionSummary,
    ActiveMode,
    Band,
    MemoryUpdateCandidate,
)
from .state_estimator import build_pass_a_prompt, build_pass_b_prompt
from .self_model import project_self_model
from .policy_gate import policy_gate


def _call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """
    Call the LLM backend. Supports Anthropic API.
    Falls back to a mock response if no API key is set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        # Mock mode for testing without API key
        return _mock_response(prompt)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=os.environ.get("MODEL_NAME", "claude-sonnet-4-20250514"),
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[generator] LLM call failed: {e}")
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """
    Return a mock response for testing without an API key.
    Detects whether this is a Pass A (JSON) or Pass B (text) call.
    """
    if "Required Output — JSON ONLY" in prompt:
        # Mock Pass A response
        return json.dumps({
            "draft_answer": "[Mock] This is a placeholder draft answer for testing.",
            "updated_state": {
                "coherence": 0.75,
                "drift": 0.10,
                "tool_overload": 0.00,
                "context_fragmentation": 0.10,
                "active_mode": "baseline",
            },
            "self_model": {
                "stability_band": "medium",
                "disruption_level": "low",
                "mode_recommendation": "baseline",
                "safe_depth": "medium",
                "state_summary": "Mock state: stable, low disruption.",
            },
            "policy_profile": {
                "style": "default",
                "depth": "medium",
                "compression": "none",
                "anchor_to_objective": False,
                "acknowledge_state_shift": False,
            },
            "memory_updates": [],
        })
    else:
        # Mock Pass B response
        return "[Mock] This is a placeholder final answer for testing without an API key."


def _parse_pass_a_output(
    raw: str, session_id: str, turn_id: int
) -> PassAOutput:
    """Parse the JSON output from Pass A into typed objects."""

    # Strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    data = json.loads(cleaned)

    # Build StateRegister from the estimated values
    st = data["updated_state"]
    updated_state = StateRegister(
        session_id=session_id,
        turn_id=turn_id,
        coherence=st["coherence"],
        drift=st["drift"],
        tool_overload=st["tool_overload"],
        context_fragmentation=st["context_fragmentation"],
        active_mode=ActiveMode(st["active_mode"]),
    )

    # Build SelfModel
    sm = data["self_model"]
    self_model = SelfModel(
        stability_band=Band(sm["stability_band"]),
        disruption_level=Band(sm["disruption_level"]),
        mode_recommendation=ActiveMode(sm["mode_recommendation"]),
        safe_depth=Band(sm["safe_depth"]),
        state_summary=sm["state_summary"],
    )

    # Build PolicyProfile
    pp = data["policy_profile"]
    policy_profile = PolicyProfile(
        style=pp["style"],
        depth=Band(pp["depth"]),
        compression=pp["compression"],
        anchor_to_objective=pp.get("anchor_to_objective", False),
        acknowledge_state_shift=pp.get("acknowledge_state_shift", False),
    )

    # Memory updates
    mem_updates = [
        MemoryUpdateCandidate(**m) for m in data.get("memory_updates", [])
    ]

    return PassAOutput(
        draft_answer=data["draft_answer"],
        updated_state=updated_state,
        self_model=self_model,
        policy_profile=policy_profile,
        memory_updates=mem_updates,
    )


def run_turn(
    user_message: str,
    session_id: str,
    turn_id: int,
    signals: ObservableSignals,
    prior_state: StateRegister,
    recent_deltas: list[StateDelta],
    session_summary: Optional[SessionSummary] = None,
    content_memory: list[dict] = [],
    boundary_context: BoundaryPolicyContext | None = None,
) -> tuple[str, PassAOutput]:
    """
    Run one complete turn: Pass A → policy gate → Pass B.

    Returns:
        (final_answer, pass_a_output)
    """

    # ── Pass A: Internal planning ──
    pass_a_prompt = build_pass_a_prompt(
        user_message=user_message,
        signals=signals,
        prior_state=prior_state,
        recent_deltas=recent_deltas,
        session_summary=session_summary,
        content_memory=content_memory,
        boundary_context=boundary_context,
    )

    raw_a = _call_llm(pass_a_prompt, max_tokens=2000)
    pass_a = _parse_pass_a_output(raw_a, session_id, turn_id)

    # ── Override self-model and policy with our own logic ──
    # (We trust our rule-based projection over LLM's self-assessment)
    our_self_model = project_self_model(pass_a.updated_state)
    our_policy = policy_gate(
        our_self_model,
        recent_deltas,
        boundary_context=boundary_context,
    )

    # Update Pass A output with our overrides
    pass_a.self_model = our_self_model
    pass_a.policy_profile = our_policy

    # ── Pass B: User-facing answer ──
    pass_b_prompt = build_pass_b_prompt(
        user_message=user_message,
        draft_answer=pass_a.draft_answer,
        self_model=our_self_model.model_dump(mode="json"),
        policy_profile=our_policy.model_dump(mode="json"),
        session_summary=session_summary,
    )

    final_answer = _call_llm(pass_b_prompt, max_tokens=4000)

    return final_answer, pass_a
