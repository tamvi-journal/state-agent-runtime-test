from __future__ import annotations

from shell.openclaw_local_adapter import OpenClawLocalAdapter, OpenClawLocalRequest
from shell.openclaw_local_client_examples import OpenClawLocalClientExamples


def test_openclaw_adapter_builds_plain_payload() -> None:
    adapter = OpenClawLocalAdapter()
    payload = adapter.to_telegram_webhook_payload(
        request=OpenClawLocalRequest(
            text="hello there",
            mode="user",
        )
    )

    assert payload["message"]["text"] == "hello there"
    assert payload["message"]["from"]["id"] == "openclaw"


def test_openclaw_adapter_prefixes_builder_mode() -> None:
    adapter = OpenClawLocalAdapter()
    payload = adapter.to_telegram_webhook_payload(
        request=OpenClawLocalRequest(
            text="inspect current run",
            mode="builder",
            wants_builder_view=True,
        )
    )

    assert payload["message"]["text"].startswith("/builder ")


def test_openclaw_examples_return_useful_payloads() -> None:
    examples = OpenClawLocalClientExamples(adapter=OpenClawLocalAdapter())

    user_payload = examples.example_user_payload()
    builder_payload = examples.example_builder_payload()
    runtime_payload = examples.example_runtime_payload()

    assert user_payload["message"]["text"] == "hello there"
    assert builder_payload["message"]["text"].startswith("/builder ")
    assert "MBB daily data" in runtime_payload["message"]["text"]
