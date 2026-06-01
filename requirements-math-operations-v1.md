# Math-Operations Requirements Document (v1)

## 1. Overview
Math-Operations v1 is a REST API that performs core mathematical operations using JSON request/response payloads.

### In Scope
- Addition
- Subtraction
- Multiplication
- Division
- Power
- Square root

### Out of Scope (v1)
- Authentication and authorization
- Rate limiting
- Batch operations

## 2. Goals
- Provide simple, consistent HTTP endpoints for mathematical operations.
- Return deterministic, machine-readable JSON responses.
- Validate all client inputs and return clear error messages.
- Ship with unit tests for all endpoints and API documentation.

## 3. Functional Requirements

### FR-1: Addition
- Endpoint: `POST /add`
- Request body:
```json
{
  "a": 10,
  "b": 5
}
```
- Success response:
```json
{
  "operation": "add",
  "result": 15
}
```

### FR-2: Subtraction
- Endpoint: `POST /subtract`
- Request body:
```json
{
  "a": 10,
  "b": 5
}
```
- Success response:
```json
{
  "operation": "subtract",
  "result": 5
}
```

### FR-3: Multiplication
- Endpoint: `POST /multiply`
- Request body:
```json
{
  "a": 10,
  "b": 5
}
```
- Success response:
```json
{
  "operation": "multiply",
  "result": 50
}
```

### FR-4: Division
- Endpoint: `POST /divide`
- Request body:
```json
{
  "a": 10,
  "b": 5
}
```
- Success response:
```json
{
  "operation": "divide",
  "result": 2
}
```
- Special rule: division by zero must return a validation/error response and must not crash the service.

### FR-5: Power
- Endpoint: `POST /power`
- Request body:
```json
{
  "base": 2,
  "exponent": 3
}
```
- Success response:
```json
{
  "operation": "power",
  "result": 8
}
```

### FR-6: Square Root
- Endpoint: `POST /sqrt`
- Request body:
```json
{
  "value": 16
}
```
- Success response:
```json
{
  "operation": "sqrt",
  "result": 4
}
```
- Special rule: negative input must return a validation/error response.

## 4. API Contract Requirements

### AR-1: Content Type
- Requests and responses must use `application/json`.

### AR-2: Request Validation
- Required fields must be present.
- Numeric fields must be valid numbers.
- Non-numeric, null, missing, and malformed payloads must be rejected with clear errors.

### AR-3: Response Shape
- Success responses include:
  - `operation` (string)
  - `result` (number)
- Error responses include:
  - `error.code` (string)
  - `error.message` (string)
  - Optional `error.details` (array/object)

### AR-4: HTTP Status Codes
- `200 OK` for successful operations.
- `400 Bad Request` for input validation failures.
- `422 Unprocessable Entity` for mathematically invalid input (for example, divide by zero, square root of negative number), if differentiated from generic validation.
- `500 Internal Server Error` for unexpected server errors.

## 5. Non-Functional Requirements

### NFR-1: Reliability
- API must return structured JSON for both success and error responses.
- Service must not crash on invalid input.

### NFR-2: Maintainability
- Endpoints should share common validation and error-handling middleware where possible.

### NFR-3: Testability
- Unit tests must cover every endpoint and key edge cases.

## 6. Error Handling Requirements
- Standardized error envelope across all endpoints.
- Human-readable messages and stable error codes.
- Global exception handling for uncaught errors.
- Operation-specific errors:
  - Division by zero
  - Square root of negative value

## 7. Testing Requirements
- Unit tests are required for all endpoints:
  - `POST /add`
  - `POST /subtract`
  - `POST /multiply`
  - `POST /divide`
  - `POST /power`
  - `POST /sqrt`
- Minimum test scenarios per endpoint:
  - Valid input returns correct result and `200`.
  - Missing fields return validation error.
  - Non-numeric input returns validation error.
- Additional edge-case tests:
  - Division by zero returns expected error status and payload.
  - Square root of negative number returns expected error status and payload.

## 8. Documentation Requirements
- Provide API documentation describing:
  - Endpoint purpose
  - Request schema with examples
  - Response schema with examples
  - Error codes and meanings
- Documentation format can be OpenAPI/Swagger or Markdown, but must be versioned in the repository.

## 9. Version Constraints
- This is v1.
- No authentication in v1.

## 10. Acceptance Criteria
- All six endpoints are implemented and reachable.
- All endpoints accept JSON and return JSON.
- Input validation exists and rejects invalid payloads.
- Error handling is consistent and documented.
- Unit tests pass for all endpoints and edge cases.
- API documentation is present in the repository.

