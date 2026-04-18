from __future__ import annotations

from openclaw_pack.adapter import OpenClawLocalAdapter
from openclaw_pack.contracts import OpenClawLocalRequest
from openclaw_pack.examples import OpenClawLocalClientExamples


def test_openclaw_adapter_builds_plain_payload() -> None:
    adapter = OpenClawLocalAdapter()
    payload = adapter.to_runtime_request(
        request=OpenClawLocalRequest(
            text="hello there",
            mode="user",
        )
    )

    assert payload["user_text"] == "hello there"
    assert payload["user_id"] == "openclaw"


def test_openclaw_adapter_prefixes_builder_mode() -> None:
    adapter = OpenClawLocalAdapter()
    payload = adapter.to_runtime_request(
        request=OpenClawLocalRequest(
            text="inspect current run",
            mode="builder",
        )
    )

    assert payload["render_mode"] == "builder"


def test_openclaw_examples_return_useful_payloads() -> None:
    examples = OpenClawLocalClientExamples(adapter=OpenClawLocalAdapter())

    user_payload = examples.example_user_payload()
    builder_payload = examples.example_builder_payload()
    runtime_payload = examples.example_runtime_payload()

    assert user_payload["user_text"] == "hello there"
    assert builder_payload["render_mode"] == "builder"
    assert runtime_payload["user_text"] == "Load MBB daily data"
