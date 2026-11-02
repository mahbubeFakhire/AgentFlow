from fastapi import Request
from fastapi.responses import JSONResponse

from agentflow.infrastructure.log_context import request_id_context


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred.",
                "request_id": request_id_context.get(),
            },
        },
    )