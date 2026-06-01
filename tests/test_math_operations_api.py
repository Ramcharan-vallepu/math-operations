"""
Comprehensive API contract tests for Math-Operations v1.

Assumption:
- FastAPI app instance is exposed as `app` from `app.main`.
  Update the import below if your module path differs.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ------------------------------
# Helpers
# ------------------------------

def assert_success_shape(body: dict[str, Any], operation: str) -> None:
    assert isinstance(body, dict)
    assert body.get("operation") == operation
    assert "result" in body
    assert isinstance(body["result"], (int, float))


def assert_structured_error(body: dict[str, Any]) -> None:
    """
    Supports either a custom error envelope:
      {"error": {"code": "...", "message": "..."}}
    or RFC7807-style problem details:
      {"type": "...", "title": "...", "status": 400, "detail": "..."}
    """
    assert isinstance(body, dict)
    if "error" in body:
        err = body["error"]
        assert isinstance(err, dict)
        assert isinstance(err.get("code"), str) and err["code"].strip()
        assert isinstance(err.get("message"), str) and err["message"].strip()
        return

    # RFC7807/problem+json compatibility.
    assert isinstance(body.get("title"), str)
    assert isinstance(body.get("detail"), str)
    assert isinstance(body.get("status"), int)


def assert_client_error_response(resp) -> None:
    assert resp.status_code in (400, 422)
    assert "application/json" in resp.headers.get("content-type", "")
    assert_structured_error(resp.json())


# ------------------------------
# Happy paths (endpoint coverage)
# ------------------------------

def test_add_happy_path() -> None:
    resp = client.post("/add", json={"a": 10, "b": 5})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), "add")
    assert resp.json()["result"] == 15


def test_subtract_happy_path() -> None:
    resp = client.post("/subtract", json={"a": 10, "b": 5})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), "subtract")
    assert resp.json()["result"] == 5


def test_multiply_happy_path() -> None:
    resp = client.post("/multiply", json={"a": 10, "b": 5})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), "multiply")
    assert resp.json()["result"] == 50


def test_divide_happy_path() -> None:
    resp = client.post("/divide", json={"a": 10, "b": 5})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), "divide")
    assert resp.json()["result"] == 2


def test_power_happy_path() -> None:
    resp = client.post("/power", json={"base": 2, "exponent": 3})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), "power")
    assert resp.json()["result"] == 8


def test_sqrt_happy_path() -> None:
    resp = client.post("/sqrt", json={"value": 16})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), "sqrt")
    assert resp.json()["result"] == 4


# ------------------------------
# Error handling and edge cases
# ------------------------------

def test_divide_by_zero_returns_structured_error() -> None:
    resp = client.post("/divide", json={"a": 10, "b": 0})
    assert resp.status_code in (400, 422)
    assert "application/json" in resp.headers.get("content-type", "")
    assert_structured_error(resp.json())


def test_negative_sqrt_returns_structured_error() -> None:
    resp = client.post("/sqrt", json={"value": -1})
    assert resp.status_code in (400, 422)
    assert "application/json" in resp.headers.get("content-type", "")
    assert_structured_error(resp.json())


# ------------------------------
# Input validation coverage
# ------------------------------

@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("/add", {"a": 10}),  # missing b
        ("/subtract", {"b": 10}),  # missing a
        ("/multiply", {"a": 10}),  # missing b
        ("/divide", {"a": 10}),  # missing b
        ("/power", {"base": 2}),  # missing exponent
        ("/sqrt", {}),  # missing value
    ],
)
def test_missing_required_fields(endpoint: str, payload: dict[str, Any]) -> None:
    resp = client.post(endpoint, json=payload)
    assert_client_error_response(resp)


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("/add", {"a": "x", "b": 1}),
        ("/subtract", {"a": 1, "b": "x"}),
        ("/multiply", {"a": "x", "b": "y"}),
        ("/divide", {"a": "x", "b": 2}),
        ("/power", {"base": "x", "exponent": 2}),
        ("/sqrt", {"value": "x"}),
    ],
)
def test_invalid_data_types(endpoint: str, payload: dict[str, Any]) -> None:
    resp = client.post(endpoint, json=payload)
    assert_client_error_response(resp)


@pytest.mark.parametrize(
    "endpoint",
    ["/add", "/subtract", "/multiply", "/divide", "/power", "/sqrt"],
)
def test_malformed_json_payloads(endpoint: str) -> None:
    malformed = '{"a": 10, "b": }'
    resp = client.post(
        endpoint,
        content=malformed,
        headers={"content-type": "application/json"},
    )
    assert resp.status_code in (400, 422)
    assert "application/json" in resp.headers.get("content-type", "")
    assert_structured_error(resp.json())


# ------------------------------
# JSON response consistency
# ------------------------------

@pytest.mark.parametrize(
    ("endpoint", "payload", "operation"),
    [
        ("/add", {"a": 1, "b": 2}, "add"),
        ("/subtract", {"a": 3, "b": 1}, "subtract"),
        ("/multiply", {"a": 2, "b": 5}, "multiply"),
        ("/divide", {"a": 8, "b": 2}, "divide"),
        ("/power", {"base": 2, "exponent": 4}, "power"),
        ("/sqrt", {"value": 25}, "sqrt"),
    ],
)
def test_success_responses_are_consistent_json(
    endpoint: str,
    payload: dict[str, Any],
    operation: str,
) -> None:
    resp = client.post(endpoint, json=payload)
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")
    assert_success_shape(resp.json(), operation)


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("/divide", {"a": 1, "b": 0}),
        ("/sqrt", {"value": -4}),
        ("/add", {"a": "bad", "b": 1}),
        ("/subtract", {"a": 2}),  # missing field
    ],
)
def test_error_responses_are_consistent_json(
    endpoint: str,
    payload: dict[str, Any],
) -> None:
    resp = client.post(endpoint, json=payload)
    assert_client_error_response(resp)


# ------------------------------
# OpenAPI availability
# ------------------------------

def test_openapi_schema_is_available_and_contains_all_paths() -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")

    body = resp.json()
    assert isinstance(body, dict)
    assert "paths" in body and isinstance(body["paths"], dict)

    for path in ("/add", "/subtract", "/multiply", "/divide", "/power", "/sqrt"):
        assert path in body["paths"], f"{path} missing from OpenAPI paths"
        assert "post" in body["paths"][path], f"{path} missing POST schema"

    # Optional contract-level assertion.
    # Each operation should advertise JSON payloads.
    for path in ("/add", "/subtract", "/multiply", "/divide", "/power", "/sqrt"):
        post_spec = body["paths"][path]["post"]
        request_body = post_spec.get("requestBody", {})
        content = request_body.get("content", {})
        assert "application/json" in content


def test_openapi_docs_ui_is_served() -> None:
    resp = client.get("/docs")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
