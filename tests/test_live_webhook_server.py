from __future__ import annotations

from server.live_webhook_server import LiveWebhookServer
from server.webhook_server_contract import WebhookHttpRequest
from server.webhook_route_table import WebhookRouteTable
from server.webhook_server_policy import WebhookServerPolicy


def build_runtime_result() -> dict:
    return {
        "final_response": "Coordination note: meaningful disagreement remains open, so action should hold until the structure is clearer.",
        "routing": {
            "lead_brain_for_action": None,
            "support_brain": None,
            "hold_for_more_input": True,
            "surface_disagreement_to_user": True,
        },
        "reconciliation": {
            "reconciliation_state": "temporary_operational_alignment",
            "operational_alignment": True,
            "epistemic_alignment": False,
        },
        "child_result": {
            "disagreement_result": {
                "disagreement_detected": True,
                "event": {"event_id": "dg_001", "still_open": True},
            },
            "tracey_result": {
                "tracey_turn": {"mode_hint": "home", "recognition_signal": True}
            },
            "seyn_result": {
                "seyn_turn": {"mode_hint": "verify", "verification_signal": True}
            },
        },
    }


def build_telegram_request(text: str = "hello there") -> WebhookHttpRequest:
    return WebhookHttpRequest(
        method="POST",
        path="/webhooks/telegram",
        headers={"content-type": "application/json"},
        json_body={
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
        },
    )


def test_route_table_resolves_telegram_path() -> None:
    routes = WebhookRouteTable()
    assert routes.resolve("/webhooks/telegram") == "telegram"
    assert routes.resolve("/webhooks/unknown") is None


def test_server_policy_rejects_unknown_route() -> None:
    policy = WebhookServerPolicy()
    decision = policy.decide(
        transport=None,
        method="POST",
        json_body={"x": 1},
    )

    assert decision.accepted is False
    assert decision.http_code == 404


def test_live_webhook_server_accepts_telegram_post() -> None:
    server = LiveWebhookServer()
    response = server.handle(
        request=build_telegram_request("/builder inspect current run"),
        runtime_result=build_runtime_result(),
    )

    assert response.status == "accepted"
    assert response.http_code == 200
    assert response.body["accepted"] is True
    assert response.body["outbound_message"] is not None


def test_live_webhook_server_rejects_non_post() -> None:
    server = LiveWebhookServer()
    response = server.handle(
        request={
            "method": "GET",
            "path": "/webhooks/telegram",
            "headers": {},
            "json_body": {},
        },
        runtime_result=build_runtime_result(),
    )

    assert response.status == "rejected"
    assert response.http_code == 405


def test_live_webhook_server_rejects_empty_json_body() -> None:
    server = LiveWebhookServer()
    response = server.handle(
        request={
            "method": "POST",
            "path": "/webhooks/telegram",
            "headers": {"content-type": "application/json"},
            "json_body": {},
        },
        runtime_result=build_runtime_result(),
    )

    assert response.status == "rejected"
    assert response.http_code == 400
