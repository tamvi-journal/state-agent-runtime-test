"""
State-Memory Agent V1 — CLI Entrypoint

Two modes:
  python main.py demo    → Run the 5-turn demo scenario (no API key needed)
  python main.py chat    → Interactive chat mode (API key required)
  python main.py state   → Print current session state + deltas

V1 Success Criterion:
  Turn sau biết mình vừa bị lệch.
"""

import sys
import json
from datetime import datetime, timezone

from app.schemas import (
    StateRegister,
    StateDelta,
    ObservableSignals,
    SessionSummary,
    ActiveMode,
)
from app.boundary_context_bridge import boundary_residue_to_policy_context
from app.state_estimator import compute_observable_signals
from app.self_model import project_self_model
from app.policy_gate import policy_gate
from app.generator import run_turn
from app.post_turn_analyzer import analyze_post_turn
from app.session_store import SessionStore
from app.memory_store import MemoryStore


# ──────────────────────────────────────────────
# Pretty printing helpers
# ──────────────────────────────────────────────

def print_state(state: StateRegister, label: str = "State"):
    print(f"\n{'─'*50}")
    print(f"  {label} (turn {state.turn_id})")
    print(f"{'─'*50}")
    print(f"  coherence:            {state.coherence:.2f}")
    print(f"  drift:                {state.drift:.2f}")
    print(f"  tool_overload:        {state.tool_overload:.2f}")
    print(f"  context_fragmentation:{state.context_fragmentation:.2f}")
    print(f"  active_mode:          {state.active_mode.value}")
    print(f"{'─'*50}")


def print_delta(delta: StateDelta):
    print(f"\n  Δ turn {delta.turn_id}:")
    print(f"    Δcoherence:     {delta.delta_coherence:+.4f}")
    print(f"    Δdrift:         {delta.delta_drift:+.4f}")
    print(f"    Δtool_overload: {delta.delta_tool_overload:+.4f}")
    print(f"    Δfragmentation: {delta.delta_context_fragmentation:+.4f}")
    print(f"    mode: {delta.prior_mode.value} → {delta.new_mode.value}")
    print(f"    cause: {delta.cause_hint}")


def print_policy(profile):
    print(f"\n  Policy: style={profile.style}, depth={profile.depth.value}, "
          f"compression={profile.compression}")
    if profile.anchor_to_objective:
        print(f"    ↳ anchor_to_objective = True")
    if profile.acknowledge_state_shift:
        print(f"    ↳ acknowledge_state_shift = True")


# ──────────────────────────────────────────────
# Demo scenario
# ──────────────────────────────────────────────

DEMO_TURNS = [
    {
        "user": (
            "I have a CSV with 50k rows of customer data. "
            "Columns are customer_id, signup_date, last_active, plan_type, "
            "support_tickets, churned. Help me figure out why customers are leaving."
        ),
        "tool_calls": 0,
        "tool_errors": 0,
        "correction": False,
    },
    {
        "user": (
            "Good plan. Let's start with the support_tickets correlation. "
            "What analysis do you recommend?"
        ),
        "tool_calls": 0,
        "tool_errors": 0,
        "correction": False,
    },
    {
        "user": (
            "Actually wait — before that, can you also help me draft a "
            "resignation letter for my job, fix a bug in my React app, "
            "and summarize this PDF about quantum computing? "
            "Oh and the CSV tool keeps erroring out."
        ),
        "tool_calls": 5,
        "tool_errors": 3,
        "correction": True,
    },
    {
        "user": (
            "OK, forget all that other stuff. Let's go back to the churn analysis."
        ),
        "tool_calls": 0,
        "tool_errors": 0,
        "correction": True,
    },
    {
        "user": "/state",  # Debug command: show state + deltas
        "tool_calls": 0,
        "tool_errors": 0,
        "correction": False,
    },
]


def run_demo():
    """Run the 5-turn demo scenario."""
    print("=" * 60)
    print("  STATE-MEMORY AGENT V1 — 5-Turn Demo")
    print("  Thesis: turn sau biết mình vừa bị lệch")
    print("=" * 60)

    session_id = f"demo_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    session_store = SessionStore(sessions_dir="./sessions")
    memory_store = MemoryStore(memory_dir="./memory/content")

    summary = session_store.start_session(
        session_id=session_id,
        objective="Help user analyze customer churn dataset",
    )

    prior_state = session_store.load_state()
    context_tokens = 500  # simulated starting context

    for i, turn_data in enumerate(DEMO_TURNS):
        turn_id = i + 1
        user_msg = turn_data["user"]

        print(f"\n{'═'*60}")
        print(f"  TURN {turn_id}")
        print(f"{'═'*60}")
        print(f"\n  User: {user_msg[:80]}{'...' if len(user_msg) > 80 else ''}")

        # Handle /state debug command
        if user_msg.strip() == "/state":
            print(f"\n  [Debug: printing state + all deltas]")
            current = session_store.load_state()
            print_state(current, "Current State")
            deltas = session_store.load_recent_deltas(n=20)
            print(f"\n  Delta History ({len(deltas)} entries):")
            for d in deltas:
                print_delta(d)
            continue

        # Simulate growing context
        context_tokens += len(user_msg.split()) * 4 + 500

        # ── Compute observable signals ──
        signals = compute_observable_signals(
            turn_id=turn_id,
            user_message=user_msg,
            tool_calls=turn_data["tool_calls"],
            tool_errors=turn_data["tool_errors"],
            user_correction=turn_data["correction"],
            context_tokens_used=context_tokens,
            context_tokens_max=128000,
            session_turn_depth=turn_id,
            prior_response_length=500 if turn_id > 1 else 0,
        )

        # ── Load recent deltas for policy gate ──
        recent_deltas = session_store.load_recent_deltas(n=5)
        boundary_context = boundary_residue_to_policy_context(
            session_store.load_boundary_residue()
        )

        # ── Run turn (Pass A → Policy Gate → Pass B) ──
        final_answer, pass_a = run_turn(
            user_message=user_msg,
            session_id=session_id,
            turn_id=turn_id,
            signals=signals,
            prior_state=prior_state,
            recent_deltas=recent_deltas,
            session_summary=summary,
            content_memory=memory_store.load_as_dicts(),
            boundary_context=boundary_context,
        )

        # ── Show results ──
        print_state(pass_a.updated_state, "Estimated State")
        print(f"\n  Self-Model: {pass_a.self_model.state_summary}")
        print_policy(pass_a.policy_profile)
        print(f"\n  Answer: {final_answer[:120]}{'...' if len(final_answer) > 120 else ''}")

        # ── Post-turn analysis ──
        new_state, delta = analyze_post_turn(
            pass_a_output=pass_a,
            prior_state=prior_state,
            session_store=session_store,
            memory_store=memory_store,
        )
        print_delta(delta)

        prior_state = new_state

    print(f"\n{'═'*60}")
    print("  Demo complete.")
    print(f"  Session files: ./sessions/{session_id}/")
    print(f"{'═'*60}")


def run_chat():
    """Interactive chat mode."""
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: Set ANTHROPIC_API_KEY in .env or environment.")
        print("For demo without API key, run: python main.py demo")
        sys.exit(1)

    session_id = f"chat_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    session_store = SessionStore(sessions_dir="./sessions")
    memory_store = MemoryStore(memory_dir="./memory/content")

    objective = input("Session objective (or press Enter to skip): ").strip()
    summary = session_store.start_session(
        session_id=session_id,
        objective=objective or "General conversation",
    )
    prior_state = session_store.load_state()
    turn_id = 0

    print("\nState-Memory Agent V1. Type /state for debug, /quit to exit.\n")

    while True:
        user_msg = input("You: ").strip()
        if not user_msg:
            continue
        if user_msg == "/quit":
            break
        if user_msg == "/state":
            current = session_store.load_state()
            print_state(current, "Current State")
            for d in session_store.load_recent_deltas(n=5):
                print_delta(d)
            continue

        turn_id += 1
        signals = compute_observable_signals(
            turn_id=turn_id,
            user_message=user_msg,
            session_turn_depth=turn_id,
        )
        recent_deltas = session_store.load_recent_deltas(n=5)
        boundary_context = boundary_residue_to_policy_context(
            session_store.load_boundary_residue()
        )

        final_answer, pass_a = run_turn(
            user_message=user_msg,
            session_id=session_id,
            turn_id=turn_id,
            signals=signals,
            prior_state=prior_state,
            recent_deltas=recent_deltas,
            session_summary=summary,
            content_memory=memory_store.load_as_dicts(),
            boundary_context=boundary_context,
        )

        print(f"\nAgent: {final_answer}\n")

        new_state, delta = analyze_post_turn(
            pass_a_output=pass_a,
            prior_state=prior_state,
            session_store=session_store,
            memory_store=memory_store,
        )
        prior_state = new_state


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py demo   → Run 5-turn demo (no API key needed)")
        print("  python main.py chat   → Interactive chat (API key required)")
        sys.exit(0)

    command = sys.argv[1].lower()
    if command == "demo":
        run_demo()
    elif command == "chat":
        run_chat()
    else:
        print(f"Unknown command: {command}")
        print("Use 'demo' or 'chat'")
