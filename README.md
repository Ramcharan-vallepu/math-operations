#Ramcharan Vallepu
# Math Operations

## Documentation

- Requirements: `docs/requirements.md`
- Architecture Decision Record: `docs/adr/ADR-001-math-operations-architecture.md`

## Implementation

- Core service: `src/math_operations/service.py`
- API endpoints in `src/math_operations/api.py`:
  - `POST /calculate`
  - `POST /tasks`
  - `GET /tasks` (supports `?status=...`)
  - `PATCH /tasks/:id` (merge-patch style partial updates)
  - `DELETE /tasks/:id`
- Tasks domain logic: `src/math_operations/tasks.py`
- Postgres migration: `db/migrations/001_create_tasks.sql`
- Tests: `tests/`

## Run API

```bash
python -m math_operations.api
```

From repo root, set module path in your shell first:

```bash
set PYTHONPATH=src
```

## Run Tests

```bash
python -m unittest discover -s tests -v
```
