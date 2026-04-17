from __future__ import annotations

from server.app_factory import AppFactory
from server.fastapi_adapter import FastAPIAdapter
from server.live_webhook_server import LiveWebhookServer
from server.runtime_provider import RuntimeProvider


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


def test_fastapi_adapter_maps_webhook_request_to_internal_response() -> None:
    adapter = FastAPIAdapter(live_webhook_server=LiveWebhookServer())
    runtime_result = RuntimeProvider().get_runtime_result()

    response = adapter.handle_webhook(
        method="POST",
        path="/webhooks/telegram",
        headers={"content-type": "application/json"},
        json_body=build_webhook_payload("/builder inspect current run"),
        runtime_result=runtime_result,
    )

    assert response["status"] == "accepted"
    assert response["http_code"] == 200
    assert response["body"]["accepted"] is True


def test_fastapi_adapter_exposes_health_and_ready() -> None:
    adapter = FastAPIAdapter(live_webhook_server=LiveWebhookServer())

    assert adapter.health()["status"] == "healthy"
    assert adapter.ready()["status"] == "ready"


def test_app_factory_handles_telegram_webhook_route() -> None:
    app = AppFactory()

    response = app.handle_telegram_webhook(
        method="POST",
        headers={"content-type": "application/json"},
        json_body=build_webhook_payload("hello there"),
    )

    assert response["status"] == "accepted"
    assert response["body"]["accepted"] is True
    assert response["body"]["outbound_message"] is not None


def test_app_factory_preserves_boundary_rejection_for_bad_method() -> None:
    app = AppFactory()

    response = app.handle_telegram_webhook(
        method="GET",
        headers={"content-type": "application/json"},
        json_body=build_webhook_payload("hello there"),
    )

    assert response["status"] == "rejected"
    assert response["http_code"] == 405
