import logging
from importlib.metadata import version

from fastapi import FastAPI
from starlette.types import ASGIApp

from agentflow.api.health import router as health_router
from agentflow.api.request_logging import RequestLoggingMiddleware
from agentflow.api.request_context import RequestContextMiddleware
from agentflow.infrastructure.logging_config import configure_logging
from agentflow.infrastructure.settings import Settings
from agentflow.api.exception_handlers import unhandled_exception_handler
from agentflow.api.lifespan import lifespan
from agentflow.api.tenants import router as tenants_router


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = Settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=version("agentflow"),
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    app.state.settings = settings
    app.include_router(health_router)
    app.include_router(tenants_router)
    
    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )

    logger.info(
        "API application created",
        extra={"event": "application_created"},
    )
    
    return RequestContextMiddleware(
        RequestLoggingMiddleware(app)
    )