from __future__ import annotations

from runtime.runtime_harness import RuntimeHarness


def test_runtime_harness_runs_the_single_worker_spine() -> None:
    result = RuntimeHarness().run(user_text="Load MBB daily data", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "passed"
    assert result["handoff_baton"]["task_focus"] == "verify bounded market-data lookup for MBB"
    assert "Main brain used market_data_worker for ticker MBB." in result["final_response"]


def test_runtime_harness_keeps_direct_response_out_of_fake_completion() -> None:
    result = RuntimeHarness().run(user_text="hello there", render_mode="user")

    assert result["verification_record"] is None
    assert result["handoff_baton"]["verification_status"] == "pending"
    assert result["gate_decision"]["decision"] == "deny"


def test_runtime_harness_routes_technical_analysis_request() -> None:
    result = RuntimeHarness().run(user_text="technical analysis for MBB", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "passed"
    assert result["handoff_baton"]["task_focus"] == "verify bounded technical analysis for MBB"
    assert "Main brain used technical_analysis_worker for ticker MBB." in result["final_response"]


def test_runtime_harness_macro_sector_mapping_requires_explicit_input_by_default() -> None:
    result = RuntimeHarness().run(user_text="macro sector mapping", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "failed"
    assert result["handoff_baton"]["task_focus"] == "verify bounded macro-sector mapping"
    assert "Main brain used macro_sector_mapping_worker." in result["final_response"]


def test_runtime_harness_macro_sector_mapping_demo_uses_explicit_sample_route() -> None:
    result = RuntimeHarness().run(user_text="macro sector mapping sample", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "passed"
    assert result["worker_payload"]["result"]["matched_signals"]
    assert "Main brain used macro_sector_mapping_worker." in result["final_response"]


def test_runtime_harness_sector_flow_requires_explicit_input_by_default() -> None:
    result = RuntimeHarness().run(user_text="sector flow", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "failed"
    assert result["handoff_baton"]["task_focus"] == "verify bounded sector-flow classification"
    assert "Main brain used sector_flow_worker." in result["final_response"]


def test_runtime_harness_sector_flow_demo_uses_explicit_sample_route() -> None:
    result = RuntimeHarness().run(user_text="sector flow sample", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "passed"
    assert result["worker_payload"]["result"]["sector_flow_board"]
    assert "Main brain used sector_flow_worker." in result["final_response"]


def test_runtime_harness_candle_volume_structure_requires_explicit_input_by_default() -> None:
    result = RuntimeHarness().run(user_text="candle volume structure", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "failed"
    assert result["handoff_baton"]["task_focus"] == "verify bounded candle-volume-structure scoring"
    assert "Main brain used candle_volume_structure_worker." in result["final_response"]


def test_runtime_harness_candle_volume_structure_demo_uses_explicit_sample_route() -> None:
    result = RuntimeHarness().run(user_text="candle volume structure sample", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "passed"
    assert result["worker_payload"]["result"]["watch_list"] or result["worker_payload"]["result"]["top_list"]
    assert "Main brain used candle_volume_structure_worker." in result["final_response"]


def test_runtime_harness_trade_memo_requires_explicit_input_by_default() -> None:
    result = RuntimeHarness().run(user_text="trade memo", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "failed"
    assert result["handoff_baton"]["task_focus"] == "verify bounded trade-memo scenario planning"
    assert "Main brain used trade_memo_worker." in result["final_response"]


def test_runtime_harness_trade_memo_demo_uses_explicit_sample_route() -> None:
    result = RuntimeHarness().run(user_text="trade memo sample", render_mode="builder")

    assert result["gate_decision"]["decision"] == "sandbox_only"
    assert result["verification_record"]["verification_status"] == "passed"
    assert result["worker_payload"]["result"]["ticker_memos"]
    assert "Main brain used trade_memo_worker." in result["final_response"]
