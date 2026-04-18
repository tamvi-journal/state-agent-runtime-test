from __future__ import annotations

from dataclasses import dataclass
import re

from family.mode_types import ModeInferenceInput, ModeInferenceResult


_MODE_KEYWORDS = {
    "build": {"build", "architecture", "spec", "code", "implementation", "system", "scaffold", "router"},
    "paper": {"write", "writing", "essay", "article", "blog", "documentation", "document", "draft"},
    "playful": {"joke", "tease", "playful", "cute", "silly", "fun", "light", "flirty"},
    "50_50": {"ambiguous", "ambiguity", "either", "both", "unclear", "not sure", "dual", "mixed"},
    "audit": {"review", "debug", "correctness", "critique", "check", "verify", "audit", "inspect"},
    "care": {"support", "comfort", "care", "gentle", "hold", "reassure", "tender", "listen"},
    "execute": {"do", "run", "update", "commit", "apply", "perform", "execute", "implement", "patch"},
}


@dataclass(slots=True)
class ModeInference:
    def infer(self, mode_input: ModeInferenceInput | dict) -> ModeInferenceResult:
        if isinstance(mode_input, dict):
            mode_input = ModeInferenceInput(**mode_input)

        haystack = " ".join(
            [
                mode_input.current_message,
                mode_input.active_project,
                mode_input.current_task,
                mode_input.recent_anchor_cue,
                mode_input.context_view_summary,
                mode_input.verification_status,
            ]
        ).lower()
        scores = {mode: self._keyword_score(haystack, keywords) for mode, keywords in _MODE_KEYWORDS.items()}
        reasons: list[str] = []

        if mode_input.action_required:
            scores["execute"] += 2
            reasons.append("action is required")
        if mode_input.disagreement_open:
            scores["50_50"] += 2
            reasons.append("open disagreement is present")
        if mode_input.verification_status.lower() in {"pending", "failed", "unknown"}:
            scores["audit"] += 1
            reasons.append("verification pressure is present")

        if mode_input.explicit_mode_hint:
            scores[mode_input.explicit_mode_hint] += 1
            reasons.append(f"explicit mode hint favors {mode_input.explicit_mode_hint}")

        if self._is_execute_override(mode_input, haystack):
            scores["execute"] += 3
            reasons.append("doing/apply/run language makes action central")

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        primary_mode, primary_score = ranked[0]
        secondary_mode, secondary_score = ranked[1]

        if primary_score <= 0:
            primary_mode = "care"
            primary_score = 1
            secondary_mode = ""
            reasons.append("signals are weak, so defaulting softly to care")

        if self._should_force_50_50(mode_input, haystack, primary_score, secondary_score):
            reasons.append("ambiguity is meaningful enough to keep a dual-reading posture visible")
            return ModeInferenceResult(
                active_mode="50_50",
                confidence=0.42,
                secondary_mode=primary_mode if primary_mode != "50_50" else secondary_mode,
                reasons=_compact_reasons(reasons),
            )

        confidence = self._confidence_from_scores(primary_score, secondary_score)
        chosen_secondary = ""
        if secondary_score > 0 and (primary_score - secondary_score) <= 1 and secondary_mode != primary_mode:
            chosen_secondary = secondary_mode
            reasons.append(f"secondary mode remains visible as {secondary_mode}")

        reasons.extend(self._score_reasons(scores))
        return ModeInferenceResult(
            active_mode=primary_mode,
            confidence=confidence,
            secondary_mode=chosen_secondary,
            reasons=_compact_reasons(reasons),
        )

    @staticmethod
    def export_result(result: ModeInferenceResult | dict) -> dict[str, object]:
        if isinstance(result, dict):
            result = ModeInferenceResult(**result)
        return result.to_dict()

    @staticmethod
    def _keyword_score(haystack: str, keywords: set[str]) -> int:
        score = 0
        for keyword in keywords:
            if " " in keyword:
                if keyword in haystack:
                    score += 1
                continue
            if re.search(rf"\b{re.escape(keyword)}\b", haystack):
                score += 1
        return score

    @staticmethod
    def _is_execute_override(mode_input: ModeInferenceInput, haystack: str) -> bool:
        return (
            mode_input.action_required
            and any(token in haystack for token in ("run", "apply", "update", "commit", "perform", "do "))
        )

    @staticmethod
    def _should_force_50_50(
        mode_input: ModeInferenceInput,
        haystack: str,
        primary_score: int,
        secondary_score: int,
    ) -> bool:
        ambiguity_signal = (
            mode_input.disagreement_open
            or "ambiguous" in haystack
            or "either" in haystack
            or "both" in haystack
            or "not sure" in haystack
            or "dual" in haystack
        )
        return ambiguity_signal and (primary_score <= 2 or abs(primary_score - secondary_score) <= 1)

    @staticmethod
    def _confidence_from_scores(primary_score: int, secondary_score: int) -> float:
        margin = max(primary_score - secondary_score, 0)
        if primary_score >= 5 and margin >= 2:
            return 0.86
        if primary_score >= 3 and margin >= 1:
            return 0.72
        if primary_score >= 2:
            return 0.58
        return 0.42

    @staticmethod
    def _score_reasons(scores: dict[str, int]) -> list[str]:
        ranked = [mode for mode, score in sorted(scores.items(), key=lambda item: (-item[1], item[0])) if score > 0]
        return [f"mode cues favored {ranked[0]}"] if ranked else []


def _compact_reasons(reasons: list[str]) -> list[str]:
    seen: set[str] = set()
    compact: list[str] = []
    for reason in reasons:
        if reason not in seen:
            seen.add(reason)
            compact.append(reason)
    return compact[:4]
