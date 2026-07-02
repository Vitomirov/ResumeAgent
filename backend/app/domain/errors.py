class DomainError(Exception):
    """Base domain error."""

    def __init__(self, message: str, code: str = "domain_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="not_found")


class ValidationError(DomainError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="validation_error")
