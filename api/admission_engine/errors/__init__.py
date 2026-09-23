class DomainError(Exception):
    code = "DOMAIN_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class UnauthorizedError(DomainError):
    code = "UNAUTHORIZED"


class ForbiddenError(DomainError):
    code = "FORBIDDEN"


class NotFoundError(DomainError):
    code = "NOT_FOUND"
