from __future__ import annotations

from fastapi.testclient import TestClient

from deploy.runtime_config import RuntimeConfig
from server.fastapi_app import create_app
from server.local_run_paths import build_local_run_paths


def build_webhook_payload(text: str = "hello there") -> dict:
    return {
        "update_id": 10001,
        "message": {
            "message_id": 501,
            "text": text,
            "chat": {"id": 777},
            "from": {
                "id": 42,
                "username": "ty_user",
                "first_name": "Ty",
            },
        },
    }


def test_health_and_ready_endpoints_work() -> None:
    client = TestClient(create_app())

    health = client.get("/health")
    ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"


def test_telegram_webhook_route_works_end_to_end() -> None:
    client = TestClient(create_app())

    response = client.post("/webhooks/telegram", json=build_webhook_payload("/builder inspect current run"))

    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["outbound_message"] is not None


def test_local_run_paths_build_expected_commands() -> None:
    config = RuntimeConfig(
        app_mode="dev",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        app_module="server.fastapi_app:app",
        reload=True,
        webhook_base_path="/webhooks",
    )

    run_paths = build_local_run_paths(config)

    assert run_paths["preferred"]["command"][0] == "uvicorn"
    assert "server.fastapi_app:app" in run_paths["preferred"]["command"]
    assert run_paths["manual"]["command"][0] == "python"
