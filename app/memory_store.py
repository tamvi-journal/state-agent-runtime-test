"""
State-Memory Agent V1 — Memory Store
Minimal flat JSON storage for durable content memory.
V1 keeps it simple: one JSON file, append-only with dedup.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from .schemas import ContentMemoryItem


class MemoryStore:
    def __init__(self, memory_dir: str = "./memory/content"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / "user.json"

        # Initialize if empty
        if not self.memory_file.exists():
            self._save([])

    def add_item(
        self,
        content: str,
        source: str = "explicit",
        item_type: str = "general",
        confidence: float = 0.8,
    ) -> ContentMemoryItem:
        """Add a new memory item. Deduplicates by content."""
        items = self.load_all()

        # Simple dedup: skip if exact content already exists
        for existing in items:
            if existing.content == content:
                existing.last_used_at = datetime.now(timezone.utc)
                self._save(items)
                return existing

        new_item = ContentMemoryItem(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            type=item_type,
            content=content,
            source=source,
            confidence=confidence,
        )
        items.append(new_item)
        self._save(items)
        return new_item

    def load_all(self) -> list[ContentMemoryItem]:
        """Load all memory items."""
        if not self.memory_file.exists():
            return []
        with open(self.memory_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [ContentMemoryItem(**item) for item in data]

    def load_as_dicts(self) -> list[dict]:
        """Load all memory items as plain dicts (for prompt injection)."""
        items = self.load_all()
        return [item.model_dump(mode="json") for item in items]

    def clear(self) -> None:
        """Clear all memory items."""
        self._save([])

    def _save(self, items: list) -> None:
        data = [
            item.model_dump(mode="json") if isinstance(item, ContentMemoryItem) else item
            for item in items
        ]
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
