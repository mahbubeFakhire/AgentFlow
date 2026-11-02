import json
import logging
from datetime import UTC, datetime
from logging.config import dictConfig
from agentflow.infrastructure.log_context import request_id_context

from agentflow.infrastructure.settings import Settings


class JsonFormatter(logging.Formatter):
    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=UTC,
            ).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        request_id = request_id_context.get()
        if request_id is not None:
            payload["request_id"] = request_id

        event = getattr(record, "event", None)
        if event is not None:
            payload["event"] = event

        http = getattr(record, "http", None)
        if http is not None:
            payload["http"] = http

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(settings: Settings) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JsonFormatter,
                    "service_name": settings.app_name,
                    "environment": settings.environment,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                    "level": settings.log_level,
                },
            },
            "loggers": {
                "agentflow": {
                    "handlers": ["console"],
                    "level": settings.log_level,
                    "propagate": False,
                },
            },
        }
    )