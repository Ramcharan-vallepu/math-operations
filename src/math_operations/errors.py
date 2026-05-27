"""Custom application errors for math operations."""

from dataclasses import dataclass


@dataclass
class MathServiceError(Exception):
    """Base error with an HTTP-like status and machine-readable code."""

    message: str
    code: str
    status: int = 400

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message}}


class ValidationError(MathServiceError):
    """Invalid input payload or unsupported operation."""

    def __init__(self, message: str, code: str = "validation_error") -> None:
        super().__init__(message=message, code=code, status=400)


class ArithmeticError(MathServiceError):
    """Arithmetic domain error."""

    def __init__(self, message: str, code: str = "arithmetic_error") -> None:
        super().__init__(message=message, code=code, status=400)
