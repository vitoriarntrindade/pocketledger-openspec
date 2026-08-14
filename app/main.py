from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import (
    AuthRateLimitMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.routers import (
    auth,
    categories,
    health,
    summary,
    transactions,
    users,
)
from app.core.config import assert_production_ready, settings
from app.core.logging import configure_logging
from app.infrastructure.tracing import configure_tracing

configure_logging()
assert_production_ready(settings)

docs_enabled = settings.environment != "production"
app = FastAPI(
    title="PocketLedger",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

cors_origins = [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuthRateLimitMiddleware)
app.add_middleware(RequestIdMiddleware)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(summary.router)
app.include_router(health.router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

configure_tracing(app)
