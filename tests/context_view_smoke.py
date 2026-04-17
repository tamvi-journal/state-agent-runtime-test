from __future__ import annotations

from family.context_view import ContextViewBuilder
from family.context_view_types import ContextViewInput


def run() -> None:
    builder = ContextViewBuilder()

    stable = builder.build(
        ContextViewInput(
            active_project="family-scaffold",
            active_mode="build",
            current_task="add context view canary",
            current_environment_state="repo clean enough for scoped canary work",
            open_obligations=["keep context compact"],
            verification_status="passed",
        )
    )
    assert stable.task_focus == "add context view canary"

    verification_heavy = builder.build(
        ContextViewInput(
            active_project="family-scaffold",
            active_mode="verify",
            current_task="confirm recent canary output",
            current_environment_state="smoke path available",
            last_verified_result="execution gate smoke passed",
            open_obligations=["do not over-claim verification"],
            verification_status="pending",
        )
    )
    assert verification_heavy.last_verified_result == "execution gate smoke passed"
    assert verification_heavy.current_risk == "verification_pressure"

    disagreement = builder.build(
        ContextViewInput(
            active_project="family-scaffold",
            active_mode="build",
            current_task="choose next canary step",
            current_environment_state="multiple narrow options available",
            open_obligations=["preserve plurality"],
            verification_status="passed",
            disagreement_events=[
                {
                    "event_id": "dg_ctx_smoke",
                    "disagreement_type": "action",
                    "severity": 0.78,
                    "still_open": True,
                }
            ],
        )
    )
    assert disagreement.shared_disagreement_status == "open:action:meaningful"

    print("context_view_smoke: ok")


if __name__ == "__main__":
    run()
