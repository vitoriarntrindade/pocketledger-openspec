import json
import logging
import sys
from datetime import datetime, timezone

from app.context import get_request_id
from app.core.config import settings


def _current_trace_id() -> str | None:
    try:
        from opentelemetry import trace

        span_context = trace.get_current_span().get_span_context()
        if span_context is not None and span_context.is_valid:
            return format(span_context.trace_id, "032x")
    except Exception:
        pass
    return None


_OPTIONAL_FIELDS = (
    "request_id",
    "trace_id",
    "http_method",
    "http_route",
    "http_status_code",
    "duration_ms",
    "user_id",
)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "service": settings.service_name,
            "environment": settings.environment,
            "message": record.getMessage(),
            "logger": record.name,
        }
        for field in _OPTIONAL_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        record.trace_id = _current_trace_id()
        return True


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.addFilter(RequestContextFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
