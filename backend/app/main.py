"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from . import __version__
from .config import Settings, get_settings
from .database import Database
from .deps import require_api_key
from .routers import alerts, assistant, medications, reports, users, vitals
from .schemas import StatusOut
from .services.assistant import HealthAssistant
from .services.notifications import Notifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("health_tracker")


def create_app(settings: Settings | None = None, database: Database | None = None) -> FastAPI:
    settings = settings or get_settings()
    database = database or Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database.create_all()
        if settings.environment == "production" and not settings.api_key:
            logger.warning("API_KEY is not set: the API is open to anyone who can reach it.")
        yield

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Track vitals and medications, get threshold-based risk flags, reminders and SOS alerts.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.db = database
    app.state.assistant = HealthAssistant(settings)
    app.state.notifier = Notifier(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-API-Key"],
    )

    @app.get("/health", response_model=StatusOut, tags=["meta"])
    def health(request: Request) -> StatusOut:
        try:
            with request.app.state.db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception:  # pragma: no cover - only when the DB is down
            db_status = "unavailable"
        s = request.app.state.settings
        return StatusOut(
            status="ok" if db_status == "ok" else "degraded",
            version=__version__,
            database=db_status,
            llm=s.llm_enabled,
            sms=s.sms_enabled,
            email=s.email_enabled,
        )

    protected = [Depends(require_api_key)]
    for router in (users.router, vitals.router, medications.router, alerts.router, assistant.router, reports.router):
        app.include_router(router, prefix="/api/v1", dependencies=protected)

    return app


app = create_app()
