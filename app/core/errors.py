class DomainError(Exception):
    """Base class for expected, business-rule-level errors."""

    code = "domain_error"
    message = "A business rule was violated."

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(DomainError):
    code = "not_found"
    message = "The requested resource was not found."


class ConflictError(DomainError):
    code = "conflict"
    message = "The request conflicts with the current state of the resource."


class ValidationError(DomainError):
    code = "validation_error"
    message = "The request was invalid."


class UnauthorizedError(DomainError):
    code = "unauthorized"
    message = "Authentication is required or has failed."
