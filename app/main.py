from __future__ import annotations

import math
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(title="Math-Operations API", version="1.0.0")


class BinaryOperationRequest(BaseModel):
    a: float
    b: float


class PowerRequest(BaseModel):
    base: float
    exponent: float


class SqrtRequest(BaseModel):
    value: float


def success(operation: str, result: float) -> dict[str, Any]:
    return {"operation": operation, "result": result}


def error_payload(
    code: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_payload(
            "VALIDATION_ERROR",
            "Invalid request payload.",
            exc.errors(),
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload("MATH_OPERATION_ERROR", message),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_payload(
            "INTERNAL_SERVER_ERROR",
            "An unexpected server error occurred.",
        ),
    )


@app.post("/add")
def add(payload: BinaryOperationRequest) -> dict[str, Any]:
    return success("add", payload.a + payload.b)


@app.post("/subtract")
def subtract(payload: BinaryOperationRequest) -> dict[str, Any]:
    return success("subtract", payload.a - payload.b)


@app.post("/multiply")
def multiply(payload: BinaryOperationRequest) -> dict[str, Any]:
    return success("multiply", payload.a * payload.b)


@app.post("/divide")
def divide(payload: BinaryOperationRequest) -> dict[str, Any]:
    if payload.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed.")
    return success("divide", payload.a / payload.b)


@app.post("/power")
def power(payload: PowerRequest) -> dict[str, Any]:
    return success("power", math.pow(payload.base, payload.exponent))


@app.post("/sqrt")
def sqrt(payload: SqrtRequest) -> dict[str, Any]:
    if payload.value < 0:
        raise HTTPException(
            status_code=400,
            detail="Square root of a negative number is not allowed.",
        )
    return success("sqrt", math.sqrt(payload.value))
