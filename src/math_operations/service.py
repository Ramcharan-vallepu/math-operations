"""Core math operations with validation and structured logging."""

from __future__ import annotations

import logging
import math
from time import perf_counter
from typing import Callable

from .errors import ArithmeticError, ValidationError

logger = logging.getLogger("math_operations")

OperationFn = Callable[[float, float], float]


def _ensure_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"'{name}' must be a number.", code="invalid_number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValidationError(f"'{name}' must be finite.", code="invalid_number")
    return numeric


def _divide(a: float, b: float) -> float:
    if b == 0:
        raise ArithmeticError("Division by zero is not allowed.", code="divide_by_zero")
    return a / b


def _modulus(a: float, b: float) -> float:
    if b == 0:
        raise ArithmeticError("Modulus by zero is not allowed.", code="modulus_by_zero")
    return a % b


OPERATIONS: dict[str, OperationFn] = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": _divide,
    "modulus": _modulus,
    "power": lambda a, b: a**b,
}


def calculate(operation: object, a: object, b: object) -> dict:
    started = perf_counter()

    if not isinstance(operation, str):
        raise ValidationError("'operation' must be a string.", code="invalid_operation")

    op = operation.strip().lower()
    fn = OPERATIONS.get(op)
    if fn is None:
        raise ValidationError(
            f"Unsupported operation '{operation}'.",
            code="unsupported_operation",
        )

    left = _ensure_number(a, "a")
    right = _ensure_number(b, "b")

    try:
        result = fn(left, right)
    except (ArithmeticError, ValidationError):
        raise
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception("Unexpected math operation failure", extra={"operation": op})
        raise ArithmeticError("Calculation failed.", code="calculation_failed") from exc

    elapsed_ms = round((perf_counter() - started) * 1000, 4)
    return {"operation": op, "a": left, "b": right, "result": result, "durationMs": elapsed_ms}
