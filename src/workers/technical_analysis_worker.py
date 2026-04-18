from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.market_data_tool import MarketDataTool
from workers.contracts import WorkerContractValidator


@dataclass(slots=True)
class TechnicalAnalysisWorker:
    """
    Bounded technical-analysis worker for the thin runtime harness.

    Responsibilities:
    - load bounded market data through MarketDataTool
    - apply a disciplined technical-analysis method
    - package structured evidence for the brain

    Non-goals:
    - no direct file access
    - no trading advice
    - no final user-facing synthesis authority
    """

    market_data_tool: MarketDataTool
    validator: WorkerContractValidator | None = None

    def __post_init__(self) -> None:
        if self.validator is None:
            self.validator = WorkerContractValidator()

    def run(self, *, ticker: str, timeframe: str = "1D") -> dict[str, Any]:
        normalized_ticker = ticker.strip().upper()
        trace: list[str] = [
            f"received technical-analysis request for ticker={normalized_ticker} timeframe={timeframe}",
            "using technical-analysis method: context -> structure -> volume -> indicators -> alignment",
            "delegating bounded data load to market_data_tool.load_market_data",
        ]
        assumptions = [
            "timeframe is inferred from the request or defaults to 1D",
            "structure is read from bounded recent rows returned by the market data tool",
            "indicators remain secondary evidence and do not override price structure",
        ]

        tool_result = self.market_data_tool.load_market_data(ticker=normalized_ticker, timeframe=timeframe)
        trace.extend(tool_result.trace)

        result = tool_result.data
        recent_rows = list(result.get("recent_rows", []))
        bars_found = int(result.get("bars_found", 0))
        warnings = list(tool_result.warnings)
        data_status = self._data_status(tool_status=tool_result.status, bars_found=bars_found)

        structure_read = "No usable chart structure was available from bounded market data."
        volume_read = "Volume behavior could not be assessed."
        indicator_read = {
            "rsi": "RSI not computed.",
            "moving_averages": "Moving-average posture could not be assessed.",
        }
        alignment_status = "unresolved"
        invalidation_condition = "No invalidation condition can be stated without usable price structure."
        confidence = 0.0

        if data_status == "missing":
            warnings.append("technical-analysis read could not proceed because bounded market data was missing")
        elif not recent_rows:
            warnings.append("market data loaded without a usable bounded row series")
        else:
            trace.append(f"technical analysis worker received {len(recent_rows)} bounded rows from market_data_tool")
            structure_read = self._structure_read(recent_rows=recent_rows)
            volume_read = self._volume_read(recent_rows=recent_rows)
            indicator_read = self._indicator_read(recent_rows=recent_rows)
            alignment_status = self._alignment_status(
                recent_rows=recent_rows,
                volume_read=volume_read,
                moving_average_read=indicator_read["moving_averages"],
            )
            invalidation_condition = self._invalidation_condition(
                recent_rows=recent_rows,
                alignment_status=alignment_status,
            )
            confidence = self._confidence(
                data_status=data_status,
                alignment_status=alignment_status,
                warning_count=len(warnings),
                row_count=len(recent_rows),
            )

            if data_status == "partial":
                warnings.append("technical-analysis context is partial because the bounded row history is short")
            if "conflict" in volume_read.lower() or alignment_status in {"mixed", "range", "unresolved"}:
                warnings.append("signals are not fully aligned, so the technical read should stay tentative")

        payload = {
            "worker_name": "technical_analysis_worker",
            "result": {
                "symbol": normalized_ticker,
                "ticker": normalized_ticker,
                "timeframe": timeframe,
                "data_status": data_status,
                "structure_read": structure_read,
                "volume_read": volume_read,
                "indicator_read": indicator_read,
                "alignment_status": alignment_status,
                "invalidation_condition": invalidation_condition,
                "bars_found": bars_found,
                "data_source": result.get("data_source", ""),
                "integrity_checks": result.get("integrity_checks", {}),
            },
            "confidence": confidence,
            "assumptions": assumptions,
            "warnings": warnings,
            "trace": trace + ["technical analysis worker packaged bounded evidence for the brain"],
            "proposed_memory_update": None,
        }
        return self.validator.validate(payload)

    @staticmethod
    def _data_status(*, tool_status: str, bars_found: int) -> str:
        if tool_status in {"not_found", "empty", "invalid"} or bars_found <= 0:
            return "missing"
        if bars_found < 5:
            return "partial"
        return "loaded"

    @staticmethod
    def _structure_read(*, recent_rows: list[dict[str, Any]]) -> str:
        latest_close = recent_rows[-1].get("close")
        first_close = recent_rows[0].get("close")
        closes = [row.get("close") for row in recent_rows if row.get("close") is not None]

        if len(closes) < 2 or latest_close is None or first_close is None:
            return "Price structure is unresolved because the bounded series is too thin."

        highs_rising = all(
            recent_rows[index]["high"] is not None
            and recent_rows[index - 1]["high"] is not None
            and recent_rows[index]["high"] >= recent_rows[index - 1]["high"]
            for index in range(1, len(recent_rows))
        )
        lows_rising = all(
            recent_rows[index]["low"] is not None
            and recent_rows[index - 1]["low"] is not None
            and recent_rows[index]["low"] >= recent_rows[index - 1]["low"]
            for index in range(1, len(recent_rows))
        )
        highs_falling = all(
            recent_rows[index]["high"] is not None
            and recent_rows[index - 1]["high"] is not None
            and recent_rows[index]["high"] <= recent_rows[index - 1]["high"]
            for index in range(1, len(recent_rows))
        )
        lows_falling = all(
            recent_rows[index]["low"] is not None
            and recent_rows[index - 1]["low"] is not None
            and recent_rows[index]["low"] <= recent_rows[index - 1]["low"]
            for index in range(1, len(recent_rows))
        )
        price_change = ((latest_close - first_close) / first_close) * 100.0 if first_close else 0.0

        if highs_rising and lows_rising:
            return (
                f"Structure leans upward with rising highs and lows across the bounded series; "
                f"latest close is {price_change:.2f}% above the first bounded close."
            )
        if highs_falling and lows_falling:
            return (
                f"Structure leans downward with falling highs and lows across the bounded series; "
                f"latest close is {abs(price_change):.2f}% below the first bounded close."
            )

        price_range = max(closes) - min(closes)
        if first_close and price_range / first_close <= 0.03:
            return "Structure looks range-bound inside a relatively tight bounded price band."

        return "Structure is mixed: direction changed within the bounded series and no clean trend dominated."

    @staticmethod
    def _volume_read(*, recent_rows: list[dict[str, Any]]) -> str:
        volumes = [row.get("volume") for row in recent_rows if row.get("volume") is not None]
        if len(volumes) < 2:
            return "Volume context is limited because the bounded series has too few parsed volume points."

        latest_volume = volumes[-1]
        average_volume = sum(volumes[:-1]) / max(len(volumes) - 1, 1)
        latest_close = recent_rows[-1].get("close")
        prior_close = recent_rows[-2].get("close")

        if latest_close is None or prior_close is None:
            return "Volume was present, but price-volume interaction is unresolved."

        if latest_close > prior_close and latest_volume > average_volume:
            return "Volume supports the latest upside move with participation above the recent average."
        if latest_close < prior_close and latest_volume > average_volume:
            return "Volume supports the latest downside move with heavier-than-average participation."
        if latest_close > prior_close and latest_volume <= average_volume:
            return "Price pushed higher, but volume confirmation was light relative to the recent average."
        if latest_close < prior_close and latest_volume <= average_volume:
            return "Price eased lower on relatively light volume, so downside pressure is not strongly confirmed."
        return "Volume and price action are not cleanly aligned."

    def _indicator_read(self, *, recent_rows: list[dict[str, Any]]) -> dict[str, str]:
        closes = [row.get("close") for row in recent_rows if row.get("close") is not None]
        moving_averages = self._moving_average_read(closes=closes)
        rsi = self._rsi_read(closes=closes)
        return {
            "rsi": rsi,
            "moving_averages": moving_averages,
        }

    @staticmethod
    def _moving_average_read(*, closes: list[float | None]) -> str:
        clean_closes = [close for close in closes if close is not None]
        if len(clean_closes) < 3:
            return "Moving-average posture is unresolved because fewer than 3 closes were available."

        short_window = clean_closes[-3:]
        short_ma = sum(short_window) / len(short_window)
        latest_close = clean_closes[-1]

        if len(clean_closes) >= 5:
            medium_window = clean_closes[-5:]
            medium_ma = sum(medium_window) / len(medium_window)
            if latest_close >= short_ma >= medium_ma:
                return "Latest close is above the short and medium moving averages, which supports trend health."
            if latest_close <= short_ma <= medium_ma:
                return "Latest close is below the short and medium moving averages, which keeps posture weak."
            return "Moving averages are compressed or crossed, which points to mixed trend posture."

        if latest_close >= short_ma:
            return "Latest close is holding above the short moving average, but medium-term context is still limited."
        return "Latest close is below the short moving average, with limited medium-term context."

    @staticmethod
    def _rsi_read(*, closes: list[float | None]) -> str:
        clean_closes = [close for close in closes if close is not None]
        if len(clean_closes) < 4:
            return "RSI not computed because the bounded close history is too short."

        deltas = [clean_closes[index] - clean_closes[index - 1] for index in range(1, len(clean_closes))]
        gains = [max(delta, 0.0) for delta in deltas]
        losses = [abs(min(delta, 0.0)) for delta in deltas]
        average_gain = sum(gains) / len(gains)
        average_loss = sum(losses) / len(losses)

        if average_loss == 0.0:
            rsi = 100.0
        else:
            rs = average_gain / average_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))

        if rsi >= 70.0:
            return f"RSI is {rsi:.1f}, which suggests stretched upside momentum."
        if rsi <= 30.0:
            return f"RSI is {rsi:.1f}, which suggests stretched downside momentum."
        if rsi >= 55.0:
            return f"RSI is {rsi:.1f}, showing constructive but not extreme momentum."
        if rsi <= 45.0:
            return f"RSI is {rsi:.1f}, showing soft momentum without an extreme washout."
        return f"RSI is {rsi:.1f}, which is broadly neutral."

    @staticmethod
    def _alignment_status(
        *,
        recent_rows: list[dict[str, Any]],
        volume_read: str,
        moving_average_read: str,
    ) -> str:
        latest_close = recent_rows[-1].get("close")
        first_close = recent_rows[0].get("close")
        if latest_close is None or first_close is None:
            return "unresolved"

        upward = latest_close > first_close
        downward = latest_close < first_close
        volume_supportive = "supports the latest upside move" in volume_read
        volume_bearish = "supports the latest downside move" in volume_read
        ma_bullish = "supports trend health" in moving_average_read or "holding above the short moving average" in moving_average_read
        ma_bearish = "keeps posture weak" in moving_average_read or "below the short moving average" in moving_average_read

        closes = [row.get("close") for row in recent_rows if row.get("close") is not None]
        if closes:
            price_range = max(closes) - min(closes)
            if first_close and price_range / first_close <= 0.03:
                return "range"

        if upward and volume_supportive and ma_bullish:
            return "bullish"
        if downward and volume_bearish and ma_bearish:
            return "bearish"
        if (upward and (volume_bearish or ma_bearish)) or (downward and (volume_supportive or ma_bullish)):
            return "mixed"
        if upward or downward:
            return "mixed"
        return "unresolved"

    @staticmethod
    def _invalidation_condition(*, recent_rows: list[dict[str, Any]], alignment_status: str) -> str:
        latest_bar = recent_rows[-1]
        latest_low = latest_bar.get("low")
        latest_high = latest_bar.get("high")

        if alignment_status == "bullish" and latest_low is not None:
            return f"Bullish alignment weakens if price loses the latest bounded swing low near {latest_low}."
        if alignment_status == "bearish" and latest_high is not None:
            return f"Bearish alignment weakens if price reclaims the latest bounded swing high near {latest_high}."
        if alignment_status == "range" and latest_high is not None and latest_low is not None:
            return (
                f"Range read breaks only if price escapes the bounded band defined by "
                f"{latest_low} to {latest_high}."
            )
        return "Invalidation remains provisional because the bounded structure is mixed or incomplete."

    @staticmethod
    def _confidence(
        *,
        data_status: str,
        alignment_status: str,
        warning_count: int,
        row_count: int,
    ) -> float:
        if data_status == "missing":
            return 0.0

        confidence = 0.72 if data_status == "loaded" else 0.48
        if alignment_status in {"mixed", "range", "unresolved"}:
            confidence -= 0.12
        if row_count < 5:
            confidence -= 0.08
        confidence -= min(warning_count, 3) * 0.05
        return max(0.15, min(confidence, 0.85))
