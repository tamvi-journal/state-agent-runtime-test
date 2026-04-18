from __future__ import annotations

from dataclasses import dataclass
import re

from family.reactivation_types import ReactivationInput, ReactivationResult


@dataclass(slots=True)
class ReactivationLayer:
    def build(self, reactivation_input: ReactivationInput | dict) -> ReactivationResult:
        if isinstance(reactivation_input, dict):
            reactivation_input = ReactivationInput(**reactivation_input)

        haystack = self._haystack(reactivation_input)
        matched_cues = self._matched_cues(reactivation_input, haystack)
        cue_support = len(matched_cues)

        restored_project = self._restored_project(reactivation_input, matched_cues)
        restored_mode = self._restored_mode(reactivation_input, cue_support)
        restored_axis_hint = self._restored_axis_hint(reactivation_input, restored_mode)
        confidence = self._confidence(reactivation_input, cue_support, restored_project, restored_mode)
        triggered = cue_support > 0 and confidence >= 0.35

        notes = self._notes(triggered, cue_support, reactivation_input)
        if not triggered and confidence < 0.35:
            restored_mode = ""
            restored_axis_hint = ""
            restored_project = restored_project if cue_support > 0 else ""

        return ReactivationResult(
            reactivation_triggered=triggered,
            matched_cues=matched_cues,
            restored_mode=restored_mode,
            restored_axis_hint=restored_axis_hint,
            restored_project=restored_project,
            confidence=confidence,
            notes=notes,
        )

    @staticmethod
    def export_result(result: ReactivationResult | dict) -> dict[str, object]:
        if isinstance(result, dict):
            result = ReactivationResult(**result)
        return result.to_dict()

    @staticmethod
    def _haystack(reactivation_input: ReactivationInput) -> str:
        parts = [reactivation_input.current_message, *reactivation_input.detected_cues]
        return " ".join(parts).lower()

    def _matched_cues(self, reactivation_input: ReactivationInput, haystack: str) -> list[str]:
        candidates = [
            reactivation_input.recent_anchor_cue,
            str(reactivation_input.compression_summary.get("anchor_cue", "")),
            reactivation_input.active_project_hint,
            str(reactivation_input.context_view.get("active_project", "")),
        ]

        matches: list[str] = []
        for candidate in candidates:
            cue = candidate.strip()
            if cue and self._cue_matches(cue, haystack) and cue not in matches:
                matches.append(cue)
        return matches[:4]

    @staticmethod
    def _cue_matches(cue: str, haystack: str) -> bool:
        cue_tokens = [token for token in re.findall(r"[a-z0-9_]+", cue.lower()) if len(token) >= 3]
        if not cue_tokens:
            return False
        return any(token in haystack for token in cue_tokens)

    @staticmethod
    def _restored_project(reactivation_input: ReactivationInput, matched_cues: list[str]) -> str:
        project_candidates = [
            reactivation_input.active_project_hint,
            str(reactivation_input.context_view.get("active_project", "")),
            str(reactivation_input.live_state.get("active_project", "")),
        ]
        for candidate in project_candidates:
            if candidate and candidate in matched_cues:
                return candidate
        return ""

    @staticmethod
    def _restored_mode(reactivation_input: ReactivationInput, cue_support: int) -> str:
        if cue_support <= 0:
            return ""
        if reactivation_input.mode_hint:
            return reactivation_input.mode_hint
        compression_hint = str(reactivation_input.compression_summary.get("next_state_hint", ""))
        if compression_hint in {"verify", "recheck"}:
            return "audit"
        if compression_hint == "hold_open":
            return "50_50"
        if compression_hint == "continue_build":
            return "build"
        return str(reactivation_input.live_state.get("active_mode", "")) or str(reactivation_input.context_view.get("active_mode", ""))

    @staticmethod
    def _restored_axis_hint(reactivation_input: ReactivationInput, restored_mode: str) -> str:
        if not restored_mode:
            return ""
        compression_hint = str(reactivation_input.compression_summary.get("next_state_hint", ""))
        if compression_hint == "hold_open" or restored_mode == "50_50":
            return "hold-open"
        if compression_hint == "verify" or restored_mode == "audit":
            return "verify-first"
        if restored_mode == "build":
            return "continue-build"
        if restored_mode == "care":
            return "return-to-anchor"
        return str(reactivation_input.live_state.get("current_axis", ""))[:48]

    @staticmethod
    def _confidence(
        reactivation_input: ReactivationInput,
        cue_support: int,
        restored_project: str,
        restored_mode: str,
    ) -> float:
        confidence = 0.10
        if cue_support >= 2:
            confidence += 0.45
        elif cue_support == 1:
            confidence += 0.25
        if restored_project:
            confidence += 0.10
        if restored_mode:
            confidence += 0.10
        if str(reactivation_input.live_state.get("coherence_level", "")) == "stable":
            confidence += 0.10
        if reactivation_input.disagreement_open:
            confidence -= 0.20
        if reactivation_input.verification_status.lower() in {"pending", "failed", "unknown"}:
            confidence -= 0.20
        return max(0.0, min(confidence, 0.95))

    @staticmethod
    def _notes(triggered: bool, cue_support: int, reactivation_input: ReactivationInput) -> str:
        if not triggered:
            return "cue support is too weak for a strong restoration claim"
        parts = [f"matched {cue_support} compact cue(s)"]
        if reactivation_input.disagreement_open:
            parts.append("confidence reduced by open disagreement")
        if reactivation_input.verification_status.lower() in {"pending", "failed", "unknown"}:
            parts.append("confidence reduced by unsettled verification")
        return "; ".join(parts)
