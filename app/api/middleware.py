import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.context import request_id_ctx_var

REQUEST_ID_HEADER = "X-Request-ID"
access_logger = logging.getLogger("app.access")
error_logger = logging.getLogger("app.unhandled")

_rate_limiter_attempts: dict[tuple[str, str], list[float]] = {}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-relevant HTTP response headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory, fixed-window rate limiter for authentication endpoints."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path not in (
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ):
            return await call_next(request)

        from app.api.error_handlers import _envelope
        from app.core.config import settings

        client_ip = request.client.host if request.client else "unknown"
        key = (client_ip, path)
        now = time.time()
        window = settings.rate_limit_window_seconds

        if key not in _rate_limiter_attempts:
            _rate_limiter_attempts[key] = []

        _rate_limiter_attempts[key] = [
            t for t in _rate_limiter_attempts[key] if now - t < window
        ]

        if (
            len(_rate_limiter_attempts[key])
            >= settings.rate_limit_max_attempts
        ):
            return JSONResponse(
                status_code=429,
                content=_envelope(
                    "rate_limited",
                    "Too many attempts, try again later.",
                ),
            )

        response = await call_next(request)
        _rate_limiter_attempts[key].append(now)
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assigns/propagates the request id and also catches unhandled exceptions.

    Unhandled exceptions must be caught here rather than via a FastAPI
    `Exception` handler: Starlette routes that specific handler to
    ServerErrorMiddleware, which sits outside every user-added middleware, so
    a handler registered there can never see this middleware's request id or
    attach the response header to it. Catching here keeps the error envelope
    and the X-Request-ID header consistent for every response, error or not.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(
            uuid.uuid4()
        )
        token = request_id_ctx_var.set(request_id)
        start = time.monotonic()
        try:
            try:
                response = await call_next(request)
            except Exception as exc:
                error_logger.error("unhandled_exception", exc_info=exc)
                response = JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "internal_error",
                            "message": "An unexpected error occurred.",
                            "request_id": request_id,
                        }
                    },
                )

            duration_ms = round((time.monotonic() - start) * 1000, 2)
            route = request.scope.get("route")
            route_path = route.path if route is not None else request.url.path
            access_logger.info(
                "request_handled",
                extra={
                    "http_method": request.method,
                    "http_route": route_path,
                    "http_status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "user_id": getattr(request.state, "user_id", None),
                },
            )
        finally:
            request_id_ctx_var.reset(token)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
