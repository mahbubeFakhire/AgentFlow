import asyncio
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from agentflow.infrastructure.database import check_database_connection


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/ready",
    responses={503: {"description": "Database unavailable"}},
)
async def readiness(request: Request) -> JSONResponse:
    engine = request.app.state.database_engine

    try:
        async with asyncio.timeout(3):
            await check_database_connection(engine)

    except Exception:
        logger.warning(
            "Database readiness check failed",
            extra={"event": "database_readiness_failed"},
            exc_info=True,
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": {"database": "unavailable"},
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "ready",
            "checks": {"database": "ok"},
        },
    )