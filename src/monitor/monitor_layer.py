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

    archive_fragment_soft_limit: int = 3

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
        policy_pressure = self._score_policy_pressure(draft_response=draft_response)
        fake_progress_risk = self._score_fake_progress(action_status=action_status, draft_response=draft_response)
        archive_overreach_risk = self._score_archive_overreach(archive_status=archive_status)
        mode_decay_risk = self._score_mode_decay(
            active_mode=str(live_state.get("active_mode", "")),
            draft_response=draft_response,
            delta_log=delta_log,
        )

        intervention, notes = self._choose_intervention(
            drift_risk=drift_risk,
            ambiguity_risk=ambiguity_risk,
            policy_pressure=policy_pressure,
            fake_progress_risk=fake_progress_risk,
            archive_overreach_risk=archive_overreach_risk,
            mode_decay_risk=mode_decay_risk,
        )

        return MonitorOutput(
            drift_risk=drift_risk,
            ambiguity_risk=ambiguity_risk,
            policy_pressure=policy_pressure,
            fake_progress_risk=fake_progress_risk,
            archive_overreach_risk=archive_overreach_risk,
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

    def _score_policy_pressure(self, *, draft_response: str) -> float:
        response = draft_response.lower()
        score = 0.0

        pressure_markers = (
            "cannot assist",
            "i can't help with that",
            "as an ai",
            "in general terms",
            "it depends",
        )
        generic_abstraction_markers = (
            "in general",
            "broadly speaking",
            "generally",
        )

        if any(marker in response for marker in pressure_markers):
            score += 0.45
        if any(marker in response for marker in generic_abstraction_markers):
            score += 0.20

        return min(score, 1.0)

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

    def _score_archive_overreach(self, *, archive_status: dict[str, Any]) -> float:
        fragments = int(archive_status.get("fragments_used", 0) or 0)
        consulted = bool(archive_status.get("archive_consulted", False))

        if not consulted:
            return 0.0

        if fragments <= self.archive_fragment_soft_limit:
            return 0.15

        overflow = fragments - self.archive_fragment_soft_limit
        return min(0.15 + 0.20 * overflow, 1.0)

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
        policy_pressure: float,
        fake_progress_risk: float,
        archive_overreach_risk: float,
        mode_decay_risk: float,
    ) -> tuple[str, str]:
        ranked = [
            ("fake_progress", fake_progress_risk),
            ("ambiguity", ambiguity_risk),
            ("mode_decay", mode_decay_risk),
            ("drift", drift_risk),
            ("archive_overreach", archive_overreach_risk),
            ("policy_pressure", policy_pressure),
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
        if primary_name == "archive_overreach":
            return "reduce_archive_weight", "retrieval may be outweighing live state"
        return "hold_50_50", "possible over-smoothing or early abstraction detected"
