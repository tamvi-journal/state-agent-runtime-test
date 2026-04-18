from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.app_factory import AppFactory
from server.operator_debug_provider import OperatorDebugProvider


def create_app() -> FastAPI:
    app = FastAPI(title="state-memory-agent", version="0.1.0")
    factory = AppFactory()
    operator_debug = OperatorDebugProvider()

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse(factory.handle_health())

    @app.get("/ready")
    async def ready() -> JSONResponse:
        return JSONResponse(factory.handle_ready())

    @app.post("/webhooks/telegram")
    async def telegram_webhook(request: Request) -> JSONResponse:
        body = await request.json()
        response = factory.handle_telegram_webhook(
            method="POST",
            headers=dict(request.headers),
            json_body=body,
        )
        return JSONResponse(content=response["body"], status_code=response["http_code"])

    @app.get("/operator/latest")
    async def operator_latest() -> JSONResponse:
        payload = operator_debug.get_operator_payload()
        return JSONResponse(content=payload.to_dict())

    @app.get("/operator/session")
    async def operator_session() -> JSONResponse:
        return JSONResponse(content=operator_debug.latest_operator_session_summary())

    @app.get("/debug/runtime-shape")
    async def debug_runtime_shape() -> JSONResponse:
        payload = operator_debug.get_debug_payload()
        return JSONResponse(content=payload.to_dict())

    @app.get("/debug/run-sample")
    async def debug_run_sample() -> JSONResponse:
        payload = operator_debug.get_debug_payload(user_text="Tracey, this is home, but verify whether MBB daily data is actually done.")
        return JSONResponse(content=payload.to_dict())

    return app


app = create_app()
