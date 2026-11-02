import logging
from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started_at = perf_counter()
        status_code: int | None = None
        response_completed = False
        exception_info = None

        async def send_with_logging(message: Message) -> None:
            nonlocal status_code, response_completed

            await send(message)

            if message["type"] == "http.response.start":
                status_code = message["status"]

            elif message["type"] == "http.response.body":
                if not message.get("more_body", False):
                    response_completed = True

        try:
            await self.app(scope, receive, send_with_logging)

        except Exception as exc:
            exception_info = (type(exc), exc, exc.__traceback__)
            raise

        finally:
            duration_ms = round(
                (perf_counter() - started_at) * 1000,
                2,
            )

            if exception_info is not None or (
                status_code is not None and status_code >= 500
            ):
                level = logging.ERROR
            elif not response_completed or (
                status_code is not None and status_code >= 400
            ):
                level = logging.WARNING
            else:
                level = logging.INFO

            logger.log(
                level,
                "HTTP request finished",
                extra={
                    "event": "http_request_finished",
                    "http": {
                        "method": scope["method"],
                        "path": scope["path"],
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "response_completed": response_completed,
                    },
                },
                exc_info=exception_info,
            )