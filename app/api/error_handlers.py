import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.context import get_request_id
from app.core.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

logger = logging.getLogger(__name__)

_STATUS_BY_ERROR = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    ValidationError: status.HTTP_400_BAD_REQUEST,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
}


def _envelope(code: str, message: str) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": get_request_id() or "",
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ):
        status_code = _STATUS_BY_ERROR.get(
            type(exc),
            status.HTTP_400_BAD_REQUEST,
        )
        # Expected, business-rule-level failures - never logged as error.
        if isinstance(exc, UnauthorizedError):
            client_ip = request.client.host if request.client else None
            logger.info(
                "auth_failed",
                extra={"client_ip": client_ip, "path": request.url.path},
            )
        else:
            logger.info("domain_error: %s", exc.code)
        return JSONResponse(
            status_code=status_code,
            content=_envelope(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ):
        logger.info("request_validation_error")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_envelope(
                "validation_error",
                "The request payload was invalid.",
            ),
        )
