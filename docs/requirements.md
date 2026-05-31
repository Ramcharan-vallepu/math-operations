# Requirements

## Project

- Name: Math Operations
- Scope: Arithmetic service plus task CRUD endpoints

## Approved Requirements

### RQ-001: Create basic arithmetic operations service

- Status: Approved
- Summary: Implement a simple math operations service supporting addition, subtraction, multiplication, and division.

### RQ-002: Implement tasks CRUD endpoints and persistence contract

- Status: Approved
- Summary: Implement task CRUD APIs with RFC 7807 errors, idempotent PATCH semantics, and Postgres schema/migration support.

## Acceptance Criteria

1. The service supports addition, subtraction, multiplication, and division.
2. Division by zero is handled with an explicit error response/contract.
3. Core arithmetic behavior is deterministic and covered by unit tests.
4. `/tasks` supports `POST`, `GET`, `PATCH`, and `DELETE` with correct success and failure status codes.
5. Error responses for `/tasks` failure paths use `application/problem+json` (RFC 7807).
6. `PATCH /tasks/:id` is idempotent for repeated equivalent documents and preserves unspecified fields.
7. Postgres schema includes a `tasks` table and a composite index on `(status, due_date)`.
8. Public usage is documented for developers.
