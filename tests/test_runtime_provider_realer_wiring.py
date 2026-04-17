from __future__ import annotations

from server.app_factory import AppFactory
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


def test_runtime_provider_returns_runtime_chain_shape() -> None:
    provider = RuntimeProvider()
    result = provider.get_runtime_result(user_text="Tracey, this is home, but verify whether MBB daily data is actually done.")

    assert "final_response" in result
    assert "routing" in result
    assert "reconciliation" in result
    assert "child_result" in result
    assert "governance_output" in result
    assert "context_view" in result


def test_runtime_provider_can_take_non_worker_text_path() -> None:
    provider = RuntimeProvider()
    result = provider.get_runtime_result(user_text="hello there")

    assert isinstance(result["final_response"], str)
    assert result["routing"] is not None


def test_app_factory_uses_realer_runtime_provider_for_webhook() -> None:
    app = AppFactory()
    response = app.handle_telegram_webhook(
        method="POST",
        headers={"content-type": "application/json"},
        json_body=build_webhook_payload("Tracey, this is home."),
    )

    assert response["status"] == "accepted"
    assert response["body"]["accepted"] is True
    assert response["body"]["outbound_message"] is not None
