"""Task persistence primitives and validation helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Protocol

ALLOWED_STATUSES = {"pending", "in_progress", "completed"}

POSTGRES_CREATE_TASKS_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    due_date TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tasks_status_check CHECK (status IN ('pending', 'in_progress', 'completed'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_due_date ON tasks (status, due_date);
""".strip()


@dataclass
class Task:
    id: int
    title: str
    status: str
    due_date: str | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "dueDate": self.due_date,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class TaskStore(Protocol):
    def create_task(self, title: str, status: str, due_date: str | None) -> dict: ...

    def list_tasks(self, status: str | None = None) -> list[dict]: ...

    def patch_task(self, task_id: int, patch: dict) -> dict | None: ...

    def delete_task(self, task_id: int) -> bool: ...


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_status(status: object) -> str:
    if not isinstance(status, str):
        raise ValueError("'status' must be a string.")
    normalized = status.strip().lower()
    if normalized not in ALLOWED_STATUSES:
        raise ValueError(
            "'status' must be one of: pending, in_progress, completed."
        )
    return normalized


def normalize_title(title: object) -> str:
    if not isinstance(title, str):
        raise ValueError("'title' must be a string.")
    normalized = title.strip()
    if not normalized:
        raise ValueError("'title' cannot be empty.")
    return normalized


def normalize_due_date(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("'dueDate' must be an ISO-8601 date-time string or null.")
    parsed_value = value.strip()
    if not parsed_value:
        raise ValueError("'dueDate' must not be empty.")
    candidate = parsed_value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("'dueDate' must be a valid ISO-8601 date-time string.") from exc
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class InMemoryTaskStore:
    """Thread-safe task store used by local runtime and tests."""

    def __init__(self) -> None:
        self._next_id = 1
        self._tasks: dict[int, Task] = {}
        self._lock = Lock()

    def create_task(self, title: str, status: str, due_date: str | None) -> dict:
        with self._lock:
            now = _utc_now_iso()
            task = Task(
                id=self._next_id,
                title=title,
                status=status,
                due_date=due_date,
                created_at=now,
                updated_at=now,
            )
            self._tasks[task.id] = task
            self._next_id += 1
            return task.to_dict()

    def list_tasks(self, status: str | None = None) -> list[dict]:
        with self._lock:
            tasks = list(self._tasks.values())
            if status is not None:
                tasks = [task for task in tasks if task.status == status]
            tasks.sort(key=lambda task: task.id)
            return [task.to_dict() for task in tasks]

    def patch_task(self, task_id: int, patch: dict) -> dict | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None

            if "title" in patch:
                task.title = normalize_title(patch["title"])
            if "status" in patch:
                task.status = normalize_status(patch["status"])
            if "dueDate" in patch:
                task.due_date = normalize_due_date(patch["dueDate"])

            task.updated_at = _utc_now_iso()
            return task.to_dict()

    def delete_task(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None


def _to_iso8601(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return str(value)


class PostgresTaskStore:
    """Postgres-backed task store using psycopg (v3)."""

    def __init__(self, dsn: str) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover - dependency availability
            raise RuntimeError(
                "Postgres task store requires psycopg. Install with: pip install psycopg[binary]"
            ) from exc

        self._psycopg = psycopg
        self._dict_row = dict_row
        self._dsn = dsn

    def _connection(self):
        return self._psycopg.connect(self._dsn, row_factory=self._dict_row)

    def _row_to_task(self, row: dict) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "status": row["status"],
            "dueDate": _to_iso8601(row.get("due_date")),
            "createdAt": _to_iso8601(row.get("created_at")),
            "updatedAt": _to_iso8601(row.get("updated_at")),
        }

    def create_task(self, title: str, status: str, due_date: str | None) -> dict:
        with self._connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, status, due_date)
                VALUES (%s, %s, %s)
                RETURNING id, title, status, due_date, created_at, updated_at
                """,
                (title, status, due_date),
            )
            row = cur.fetchone()
            conn.commit()
        return self._row_to_task(row)

    def list_tasks(self, status: str | None = None) -> list[dict]:
        with self._connection() as conn, conn.cursor() as cur:
            if status is None:
                cur.execute(
                    """
                    SELECT id, title, status, due_date, created_at, updated_at
                    FROM tasks
                    ORDER BY id
                    """
                )
            else:
                cur.execute(
                    """
                    SELECT id, title, status, due_date, created_at, updated_at
                    FROM tasks
                    WHERE status = %s
                    ORDER BY id
                    """,
                    (status,),
                )
            rows = cur.fetchall()
        return [self._row_to_task(row) for row in rows]

    def patch_task(self, task_id: int, patch: dict) -> dict | None:
        with self._connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, status, due_date, created_at, updated_at
                FROM tasks
                WHERE id = %s
                """,
                (task_id,),
            )
            current = cur.fetchone()
            if current is None:
                return None

            title = normalize_title(patch["title"]) if "title" in patch else current["title"]
            status = normalize_status(patch["status"]) if "status" in patch else current["status"]
            due_date = normalize_due_date(patch["dueDate"]) if "dueDate" in patch else current["due_date"]

            cur.execute(
                """
                UPDATE tasks
                SET title = %s, status = %s, due_date = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, title, status, due_date, created_at, updated_at
                """,
                (title, status, due_date, task_id),
            )
            updated = cur.fetchone()
            conn.commit()
        return self._row_to_task(updated)

    def delete_task(self, task_id: int) -> bool:
        with self._connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted


def build_default_task_store() -> TaskStore:
    dsn = os.getenv("TASKS_DATABASE_URL")
    if not dsn:
        return InMemoryTaskStore()
    return PostgresTaskStore(dsn)
