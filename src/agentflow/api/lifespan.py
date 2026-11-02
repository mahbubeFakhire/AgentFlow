import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from agentflow.infrastructure.database import (
    create_database_engine,
    create_session_factory,
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_database_engine(app.state.settings)

    try:
        app.state.database_engine = engine
        app.state.session_factory = create_session_factory(engine)

        logger.info(
            "Application started",
            extra={"event": "application_started"},
        )

        yield

    finally:
        await engine.dispose()

        logger.info(
            "Database engine disposed",
            extra={"event": "database_engine_disposed"},
        )