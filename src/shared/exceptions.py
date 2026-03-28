"""Shared exceptions used across all domains."""


class DomainError(Exception):
    """Base domain error."""
    pass


class NotFoundError(DomainError):
    """Entity not found."""
    pass


class ValidationError(DomainError):
    """Business validation error."""
    pass


class AuthorizationError(DomainError):
    """Unauthorized access."""
    pass
