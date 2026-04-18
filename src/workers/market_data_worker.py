from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.market_data_tool import MarketDataTool
from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class MarketDataWorker:
    """
    First bounded worker.

    Responsibilities:
    - apply market-data task logic
    - call the bounded market data tool
    - return a strict worker contract payload

    Non-goals:
    - no trading advice
    - no ranking
    - no interpretation beyond data integrity
    """

    market_data_tool: MarketDataTool
    validator: WorkerContractValidator | None = None

    def __post_init__(self) -> None:
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(self, *, ticker: str, timeframe: str = "1D") -> dict[str, Any]:
        trace: list[str] = [
            f"received request for ticker={ticker} timeframe={timeframe}",
            "delegating bounded execution to market_data_tool.load_market_data",
        ]
        assumptions: list[str] = [
            "tool owns raw csv read, parse, normalize, and integrity-check work",
            "timeframe is informational unless explicitly encoded in file",
            "worker packages tool evidence but does not claim upstream market truth",
        ]
        tool_result = self.market_data_tool.load_market_data(ticker=ticker, timeframe=timeframe)
        trace.extend(tool_result.trace)

        confidence = 0.96
        if tool_result.status == "not_found":
            confidence = 0.0
        elif tool_result.status == "empty":
            confidence = 0.2
        elif tool_result.status == "invalid":
            confidence = 0.1
        elif tool_result.data.get("bars_found", 0) == 0:
            confidence = 0.4
        elif tool_result.warnings:
            confidence = 0.75

        payload = {
            "worker_name": "market_data_worker",
            "result": tool_result.data,
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": tool_result.warnings,
            "trace": trace + ["worker packaged bounded tool output as evidence for the brain"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)
