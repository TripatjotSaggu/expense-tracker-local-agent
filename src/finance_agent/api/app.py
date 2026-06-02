from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from finance_agent.api.routes_health import router as health_router
from finance_agent.api.routes_plaid import router as plaid_router
from finance_agent.api.routes_summary import router as summary_router
from finance_agent.api.routes_ui import router as ui_router
from finance_agent.storage.db import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Local Finance Agent API",
        version="0.2.0",
        description="Local backend for Plaid ingestion and local LLM summaries.",
        lifespan=lifespan,
    )
    app.include_router(ui_router)
    app.include_router(health_router)
    app.include_router(plaid_router)
    app.include_router(summary_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run("finance_agent.api.app:app", host="127.0.0.1", port=8000, reload=False)
