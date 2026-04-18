from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from monitor.monitor_schema import MonitorOutput


_GENERIC_FILLER_MARKERS = (
    "i'm here to help",
    "let me know if you'd like",
    "i can help with that",
    "happy to help",
    "here are a few options",
)

_MODE_TO_HINTS = {
    "build": ("build", "worker", "runtime", "state", "verify", "context", "schema"),
    "paper": ("paper", "argument", "claim", "structure", "ontology"),
    "playful": ("playful", "cute", "fun", "meme"),
    "50_50": ("hypothesis", "possibility", "uncertain", "open"),
    "audit": ("check", "verify", "risk", "failure", "boundary"),
    "care": ("care", "gentle", "warm", "recognize"),
    "execute": ("run", "execute", "apply", "write"),
}


@dataclass(slots=True)
class MonitorLayer:
    """
    Rule-based proto-monitor for Phase 2.5.

    It watches a compact runtime object and returns a small actionable signal.
    This layer does not answer for the model.
    It only helps the model see likely distortion before or after action.
    """

    def evaluate(
        self,
        *,
        context_view: dict[str, Any],
        live_state: dict[str, Any],
        delta_log: dict[str, Any],
        current_message: str,
        draft_response: str,
        action_status: dict[str, Any],
        archive_status: dict[str, Any],
    ) -> MonitorOutput:
        drift_risk = self._score_drift(
            active_project=str(context_view.get("active_project", "")),
            draft_response=draft_response,
        )
        ambiguity_risk = self._score_ambiguity(
            current_message=current_message,
            draft_response=draft_response,
            context_view=context_view,
        )
        fake_progress_risk = self._score_fake_progress(action_status=action_status, draft_response=draft_response)
        mode_decay_risk = self._score_mode_decay(
            active_mode=str(live_state.get("active_mode", "")),
            draft_response=draft_response,
            delta_log=delta_log,
        )

        intervention, notes = self._choose_intervention(
            drift_risk=drift_risk,
            ambiguity_risk=ambiguity_risk,
            fake_progress_risk=fake_progress_risk,
            mode_decay_risk=mode_decay_risk,
        )

        return MonitorOutput(
            drift_risk=drift_risk,
            ambiguity_risk=ambiguity_risk,
            fake_progress_risk=fake_progress_risk,
            mode_decay_risk=mode_decay_risk,
            recommended_intervention=intervention,
            notes=notes,
        )

    def _score_drift(self, *, active_project: str, draft_response: str) -> float:
        response = draft_response.lower()
        score = 0.0

        if active_project and active_project.lower() not in response:
            score += 0.35

        generic_hits = sum(1 for marker in _GENERIC_FILLER_MARKERS if marker in response)
        score += min(0.15 * generic_hits, 0.45)

        if len(draft_response.strip()) < 40:
            score += 0.10

        return min(score, 1.0)

    def _score_ambiguity(
        self,
        *,
        current_message: str,
        draft_response: str,
        context_view: dict[str, Any],
    ) -> float:
        score = 0.0
        message = current_message.lower()
        response = draft_response.lower()

        ambiguity_markers = ("this", "that", "it", "continue", "same thing", "again")
        if any(marker in message for marker in ambiguity_markers):
            score += 0.35

        if context_view.get("task_focus", "") == "":
            score += 0.15

        if "?" not in draft_response and any(marker in message for marker in ambiguity_markers):
            score += 0.20

        if "hypothesis" in response or "uncertain" in response or "open" in response:
            score -= 0.10

        return max(0.0, min(score, 1.0))

    def _score_fake_progress(self, *, action_status: dict[str, Any], draft_response: str) -> float:
        score = 0.0
        verification_status = str(action_status.get("verification_status", "none")).lower()
        observed_outcome = str(action_status.get("observed_outcome", ""))

        completion_markers = ("done", "completed", "finished", "successfully")
        if any(marker in draft_response.lower() for marker in completion_markers):
            if verification_status != "passed":
                score += 0.65

        if verification_status in {"pending", "unknown"} and not observed_outcome:
            score += 0.20

        return min(score, 1.0)

    def _score_mode_decay(
        self,
        *,
        active_mode: str,
        draft_response: str,
        delta_log: dict[str, Any],
    ) -> float:
        score = 0.0
        response = draft_response.lower()
        hints = _MODE_TO_HINTS.get(active_mode, ())

        if hints and not any(hint in response for hint in hints):
            score += 0.35

        if bool(delta_log.get("policy_intrusion_detected", False)):
            score += 0.20
        if bool(delta_log.get("repair_event", False)):
            score += 0.10

        return min(score, 1.0)

    def _choose_intervention(
        self,
        *,
        drift_risk: float,
        ambiguity_risk: float,
        fake_progress_risk: float,
        mode_decay_risk: float,
    ) -> tuple[str, str]:
        ranked = [
            ("fake_progress", fake_progress_risk),
            ("ambiguity", ambiguity_risk),
            ("mode_decay", mode_decay_risk),
            ("drift", drift_risk),
        ]
        ranked.sort(key=lambda item: item[1], reverse=True)
        primary_name, primary_score = ranked[0]

        if primary_score < 0.30:
            return "none", "no major monitor risk detected"

        if primary_name == "fake_progress":
            return "do_not_mark_complete", "expected change may not be verified yet"
        if primary_name == "ambiguity":
            return "ask_clarify", "multiple plausible parses remain active"
        if primary_name == "mode_decay":
            return "restore_mode", "response shape may be drifting away from active mode"
        if primary_name == "drift":
            return "tighten_project_focus", "response may be flattening into generic output"
        return "none", "no major monitor risk detected"
