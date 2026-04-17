from __future__ import annotations

from fastapi.testclient import TestClient

from server.fastapi_app import create_app
from server.operator_debug_provider import OperatorDebugProvider


def test_operator_provider_returns_operator_payload() -> None:
    provider = OperatorDebugProvider()
    payload = provider.get_operator_payload(user_text="Tracey, this is home.")

    assert payload.operator_snapshot is not None
    assert payload.dashboard_snapshot is not None
    assert "[operator-console]" in payload.rendered_console


def test_debug_provider_returns_runtime_shape() -> None:
    provider = OperatorDebugProvider()
    payload = provider.get_debug_payload(user_text="hello there")

    assert payload.runtime_shape["has_final_response"] is True
    assert payload.runtime_shape["has_routing"] is True
    assert isinstance(payload.notes, list)


def test_fastapi_operator_and_debug_endpoints_work() -> None:
    client = TestClient(create_app())

    operator_resp = client.get("/operator/latest")
    session_resp = client.get("/operator/session")
    debug_resp = client.get("/debug/runtime-shape")
    sample_resp = client.get("/debug/run-sample")

    assert operator_resp.status_code == 200
    assert session_resp.status_code == 200
    assert debug_resp.status_code == 200
    assert sample_resp.status_code == 200

    operator_body = operator_resp.json()
    debug_body = debug_resp.json()

    assert "operator_snapshot" in operator_body
    assert "dashboard_snapshot" in operator_body
    assert "runtime_shape" in debug_body
    assert debug_body["runtime_shape"]["has_context_view"] is True
