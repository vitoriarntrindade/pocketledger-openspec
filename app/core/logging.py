import json
import logging
import sys
from datetime import UTC, datetime

from opentelemetry import trace

from app.context import get_request_id
from app.core.config import settings


def _current_trace_id() -> str | None:
    """Return the active span's trace id, or None if none is recording.

    There is deliberately no exception guard here. This runs inside a
    logging filter, where raising would break logging itself and where
    catching-then-logging would recurse. The OpenTelemetry API returns an
    invalid span rather than raising when no provider is configured, so
    the failure mode this would guard against does not occur — and if
    something genuinely unexpected did happen, silently returning None
    would hide it forever.
    """
    span_context = trace.get_current_span().get_span_context()
    if span_context.is_valid:
        return format(span_context.trace_id, "032x")
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
            "timestamp": datetime.fromtimestamp(
                record.created, tz=UTC
            ).isoformat(),
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
