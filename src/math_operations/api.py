"""HTTP API for math operations and task management using Python standard library."""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .errors import MathServiceError
from .service import calculate
from .tasks import (
    TaskStore,
    build_default_task_store,
    normalize_due_date,
    normalize_status,
    normalize_title,
)

logger = logging.getLogger("math_operations")


class MathRequestHandler(BaseHTTPRequestHandler):
    server_version = "MathOperationsHTTP/1.0"
    task_store = build_default_task_store()

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_problem(
        self,
        status: int,
        title: str,
        detail: str,
        type_: str = "about:blank",
        instance: str | None = None,
    ) -> None:
        payload = {
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
        }
        if instance is not None:
            payload["instance"] = instance
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/problem+json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_object_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        payload = json.loads(raw_body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return payload

    def _task_id_from_path(self, path: str) -> int | None:
        prefix = "/tasks/"
        if not path.startswith(prefix):
            return None
        task_id_str = path[len(prefix) :]
        if not task_id_str.isdigit():
            return None
        return int(task_id_str)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/calculate":
            self._handle_calculate()
            return
        if parsed.path == "/tasks":
            self._handle_create_task()
            return
        self._send_problem(
            404,
            "Route not found",
            "No endpoint exists for the requested path.",
            instance=self.path,
        )

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/tasks":
            self._handle_list_tasks(parsed.query)
            return
        self._send_problem(
            404,
            "Route not found",
            "No endpoint exists for the requested path.",
            instance=self.path,
        )

    def do_PATCH(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        task_id = self._task_id_from_path(parsed.path)
        if task_id is None:
            self._send_problem(
                404,
                "Route not found",
                "No endpoint exists for the requested path.",
                instance=self.path,
            )
            return
        self._handle_patch_task(task_id)

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        task_id = self._task_id_from_path(parsed.path)
        if task_id is None:
            self._send_problem(
                404,
                "Route not found",
                "No endpoint exists for the requested path.",
                instance=self.path,
            )
            return
        self._handle_delete_task(task_id)

    def _handle_calculate(self) -> None:
        try:
            payload = self._read_json_object_body()
            response = calculate(
                operation=payload.get("operation"),
                a=payload.get("a"),
                b=payload.get("b"),
            )
            self._send_json(200, response)
        except MathServiceError as err:
            logger.error(
                "Math operation request failed",
                extra={"path": self.path, "error_code": err.code, "error_message": err.message},
            )
            self._send_json(err.status, err.to_dict())
        except (ValueError, json.JSONDecodeError):
            self._send_json(
                400,
                {
                    "error": {
                        "code": "invalid_json",
                        "message": "Request body must be valid JSON object.",
                    }
                },
            )
        except Exception:  # pragma: no cover - safety net
            logger.exception("Unhandled API failure")
            self._send_json(
                500,
                {"error": {"code": "internal_error", "message": "Unexpected server error."}},
            )

    def _handle_create_task(self) -> None:
        try:
            payload = self._read_json_object_body()
            title = normalize_title(payload.get("title"))
            status = normalize_status(payload.get("status", "pending"))
            due_date = normalize_due_date(payload.get("dueDate"))
            task = self.task_store.create_task(title=title, status=status, due_date=due_date)
            self._send_json(201, task)
        except (ValueError, json.JSONDecodeError) as err:
            self._send_problem(
                400,
                "Invalid request body",
                str(err),
                instance=self.path,
            )
        except Exception:  # pragma: no cover - safety net
            logger.exception("Create task failed")
            self._send_problem(
                500,
                "Internal server error",
                "Unexpected server error.",
                instance=self.path,
            )

    def _handle_list_tasks(self, raw_query: str) -> None:
        try:
            query = parse_qs(raw_query)
            status = None
            if "status" in query:
                status = normalize_status(query["status"][0])
            tasks = self.task_store.list_tasks(status=status)
            self._send_json(200, {"items": tasks})
        except ValueError as err:
            self._send_problem(
                400,
                "Invalid query",
                str(err),
                instance=self.path,
            )
        except Exception:  # pragma: no cover - safety net
            logger.exception("List tasks failed")
            self._send_problem(
                500,
                "Internal server error",
                "Unexpected server error.",
                instance=self.path,
            )

    def _handle_patch_task(self, task_id: int) -> None:
        allowed_fields = {"title", "status", "dueDate"}
        try:
            patch = self._read_json_object_body()
            unknown_fields = set(patch) - allowed_fields
            if unknown_fields:
                unknown = ", ".join(sorted(unknown_fields))
                raise ValueError(f"Unsupported patch field(s): {unknown}.")

            updated_task = self.task_store.patch_task(task_id=task_id, patch=patch)
            if updated_task is None:
                self._send_problem(
                    404,
                    "Task not found",
                    f"No task exists for id {task_id}.",
                    type_="https://example.com/problems/not-found",
                    instance=self.path,
                )
                return
            self._send_json(200, updated_task)
        except (ValueError, json.JSONDecodeError) as err:
            self._send_problem(
                400,
                "Invalid patch document",
                str(err),
                instance=self.path,
            )
        except Exception:  # pragma: no cover - safety net
            logger.exception("Patch task failed")
            self._send_problem(
                500,
                "Internal server error",
                "Unexpected server error.",
                instance=self.path,
            )

    def _handle_delete_task(self, task_id: int) -> None:
        try:
            deleted = self.task_store.delete_task(task_id)
            if not deleted:
                self._send_problem(
                    404,
                    "Task not found",
                    f"No task exists for id {task_id}.",
                    type_="https://example.com/problems/not-found",
                    instance=self.path,
                )
                return
            self.send_response(204)
            self.end_headers()
        except Exception:  # pragma: no cover - safety net
            logger.exception("Delete task failed")
            self._send_problem(
                500,
                "Internal server error",
                "Unexpected server error.",
                instance=self.path,
            )

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    task_store: TaskStore | None = None,
) -> ThreadingHTTPServer:
    class RequestHandler(MathRequestHandler):
        pass

    if task_store is not None:
        RequestHandler.task_store = task_store
    return ThreadingHTTPServer((host, port), RequestHandler)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    logging.basicConfig(level=logging.INFO)
    server = create_server(host, port)
    logger.info("Starting math operations API on http://%s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down math operations API")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
