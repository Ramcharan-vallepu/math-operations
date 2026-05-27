#Ramcharan
# Math Operations

## Documentation

- Requirements: `docs/requirements.md`
- Architecture Decision Record: `docs/adr/ADR-001-math-operations-architecture.md`

## Implementation

- Core service: `src/math_operations/service.py`
- API endpoint: `POST /calculate` in `src/math_operations/api.py`
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
