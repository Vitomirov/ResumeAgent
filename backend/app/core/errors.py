from app.domain.errors import DomainError, NotFoundError, ValidationError

AppError = DomainError

__all__ = ["AppError", "DomainError", "NotFoundError", "ValidationError"]
