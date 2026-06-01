# Math-Operations Test Coverage Matrix

This matrix maps each approved requirement to concrete tests in `tests/test_math_operations_api.py`.

## Legend
- Req IDs align to the approved requirements/story:
  - Endpoint correctness (`/add`, `/subtract`, `/multiply`, `/divide`, `/power`, `/sqrt`)
  - Structured errors (division by zero, negative sqrt)
  - Input validation (missing/invalid/malformed)
  - Consistent JSON responses
  - HTTP status code validation
  - OpenAPI documentation availability

## Matrix

| Requirement | Test(s) | Coverage Type |
|---|---|---|
| `POST /add` returns correct addition results | `test_add_happy_path`, `test_success_responses_are_consistent_json[/add]` | Happy path + contract |
| `POST /subtract` returns correct subtraction results | `test_subtract_happy_path`, `test_success_responses_are_consistent_json[/subtract]` | Happy path + contract |
| `POST /multiply` returns correct multiplication results | `test_multiply_happy_path`, `test_success_responses_are_consistent_json[/multiply]` | Happy path + contract |
| `POST /divide` returns correct division results | `test_divide_happy_path`, `test_success_responses_are_consistent_json[/divide]` | Happy path + contract |
| `POST /power` returns correct exponentiation results | `test_power_happy_path`, `test_success_responses_are_consistent_json[/power]` | Happy path + contract |
| `POST /sqrt` returns correct square root results | `test_sqrt_happy_path`, `test_success_responses_are_consistent_json[/sqrt]` | Happy path + contract |
| Division by zero returns structured error response | `test_divide_by_zero_returns_structured_error`, `test_error_responses_are_consistent_json[/divide]` | Edge case + error contract |
| Negative square root returns structured error response | `test_negative_sqrt_returns_structured_error`, `test_error_responses_are_consistent_json[/sqrt]` | Edge case + error contract |
| Input validation rejects missing values | `test_missing_required_fields` (parametrized for all endpoints) | Validation |
| Input validation rejects invalid data types | `test_invalid_data_types` (parametrized for all endpoints) | Validation |
| Input validation rejects malformed JSON payloads | `test_malformed_json_payloads` (parametrized for all endpoints) | Validation |
| All endpoints return consistent JSON success responses | `test_success_responses_are_consistent_json` | Contract consistency |
| All endpoints return consistent JSON error responses | `test_error_responses_are_consistent_json`, `assert_structured_error` helper | Contract consistency |
| HTTP status codes are validated for success + client errors | All tests assert status; centralized checks in `assert_client_error_response` | Status validation |
| OpenAPI documentation is generated automatically | `test_openapi_schema_is_available_and_contains_all_paths`, `test_openapi_docs_ui_is_served` | Documentation |

## Notes On Expected Files

To run this suite, ensure these files/modules exist:

- `tests/test_math_operations_api.py` (created)
- `app/main.py` exporting `app` (FastAPI instance)
- Optional test config:
  - `pytest.ini` (markers/options)
  - `requirements-dev.txt` or equivalent with `pytest`, `fastapi`, `httpx`

