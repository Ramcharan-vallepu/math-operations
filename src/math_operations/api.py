"""HTTP API for math operations using Python standard library."""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .errors import MathServiceError
from .service import calculate

logger = logging.getLogger("math_operations")


class MathRequestHandler(BaseHTTPRequestHandler):
    server_version = "MathOperationsHTTP/1.0"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/calculate":
            self._send_json(404, {"error": {"code": "not_found", "message": "Route not found."}})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(raw_body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Body must be a JSON object.")

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

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), MathRequestHandler)


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
