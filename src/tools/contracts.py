from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolRequest:
    """
    Minimal tool invocation contract for the active harness.

    A tool request describes the bounded action a worker is asking a tool to
    perform. It is intentionally small and does not imply any registry,
    plugin, or discovery system.
    """

    tool_name: str
    action_name: str
    target: str
    arguments: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("tool_name must be a non-empty string")
        if not isinstance(self.action_name, str) or not self.action_name.strip():
            raise ValueError("action_name must be a non-empty string")
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("target must be a non-empty string")
        if not isinstance(self.arguments, dict):
            raise TypeError("arguments must be a dictionary")


@dataclass(slots=True)
class ToolResult:
    """
    Minimal bounded execution result for the active harness.

    Tool results report what the tool attempted, where it acted, the structured
    data it produced, and any warnings or errors. Verification still happens
    later in the runtime.
    """

    tool_name: str
    action_name: str
    target: str
    status: str
    data: dict[str, Any]
    trace: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("tool_name must be a non-empty string")
        if not isinstance(self.action_name, str) or not self.action_name.strip():
            raise ValueError("action_name must be a non-empty string")
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("target must be a non-empty string")
        if not isinstance(self.status, str) or not self.status.strip():
            raise ValueError("status must be a non-empty string")
        if not isinstance(self.data, dict):
            raise TypeError("data must be a dictionary")
        if not isinstance(self.trace, list):
            raise TypeError("trace must be a list")
        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list")
        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("error must be a string or None")
