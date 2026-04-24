from __future__ import annotations

from typing import Any

from state_memory.contracts import lifecycle_rank


def reactivate_state_memories(
    *,
    records: list[dict[str, Any]],
    cue_text: str,
    session_id: str = "",
    scope_prefix: str = "",
    limit: int = 5,
) -> list[dict[str, Any]]:
    haystack = str(cue_text or "").lower()
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for index, record in enumerate(records):
        lifecycle_status = str(record.get("lifecycle_status", "observed"))
        if lifecycle_status in {"deprecated", "invalidated"}:
            continue
        if session_id and str(record.get("session_id", "")) not in {"", session_id}:
            continue
        if scope_prefix and not str(record.get("scope", "")).startswith(scope_prefix):
            continue

        terms = _record_terms(record)
        if not terms:
            continue
        match_count = sum(1 for term in terms if term and term in haystack)
        if match_count <= 0:
            continue
        score = match_count * 10 - lifecycle_rank(lifecycle_status)
        scored.append((score, index, record))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    selected = [record for _, _, record in scored]
    if limit <= 0:
        return selected
    return selected[:limit]


def _record_terms(record: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    for field in ("summary", "event_type", "scope", "source"):
        value = str(record.get(field, "")).lower().strip()
        if value:
            terms.add(value)
            terms.update(token for token in value.replace("/", " ").replace("_", " ").split() if len(token) >= 3)
    for tag in record.get("tags", []) or []:
        value = str(tag).lower().strip()
        if value:
            terms.add(value)
    evidence = record.get("evidence", {})
    if isinstance(evidence, dict):
        for value in evidence.values():
            text = str(value).lower().strip()
            if text and len(text) < 80:
                terms.add(text)
    return terms
