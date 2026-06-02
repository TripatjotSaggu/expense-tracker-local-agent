from fastapi import FastAPI
import uvicorn

from finance_agent.api.routes_health import router as health_router
from finance_agent.api.routes_plaid import router as plaid_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Local Finance Agent API",
        version="0.2.0",
        description="Local backend for Plaid ingestion and local LLM summaries.",
    )
    app.include_router(health_router)
    app.include_router(plaid_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run("finance_agent.api.app:app", host="127.0.0.1", port=8000, reload=False)
