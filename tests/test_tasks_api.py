import json
import os
import sys
import threading
import unittest
from urllib import request
from urllib.error import HTTPError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from math_operations.api import create_server
from math_operations.tasks import InMemoryTaskStore


class TestTasksAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0, task_store=InMemoryTaskStore())
        cls.host, cls.port = cls.server.server_address
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _request_json(self, method, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(
            f"http://{self.host}:{self.port}{path}",
            method=method,
            data=data,
            headers=headers,
        )

        try:
            with request.urlopen(req) as response:
                body_text = response.read().decode("utf-8")
                body = json.loads(body_text) if body_text else None
                return response.getcode(), dict(response.headers), body
        except HTTPError as err:
            body_text = err.read().decode("utf-8")
            body = json.loads(body_text) if body_text else None
            return err.code, dict(err.headers), body

    def test_post_tasks_success(self):
        status, _, body = self._request_json(
            "POST",
            "/tasks",
            {"title": "Implement endpoints", "status": "pending"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(body["title"], "Implement endpoints")
        self.assertEqual(body["status"], "pending")
        self.assertIn("id", body)

    def test_post_tasks_error_path_rfc7807(self):
        status, headers, body = self._request_json("POST", "/tasks", {"status": "pending"})
        self.assertEqual(status, 400)
        self.assertEqual(headers.get("Content-Type"), "application/problem+json")
        self.assertEqual(body["status"], 400)
        self.assertEqual(body["title"], "Invalid request body")

    def test_get_tasks_with_status_filter(self):
        self._request_json("POST", "/tasks", {"title": "A", "status": "pending"})
        self._request_json("POST", "/tasks", {"title": "B", "status": "completed"})
        status, _, body = self._request_json("GET", "/tasks?status=completed")
        self.assertEqual(status, 200)
        self.assertEqual(len(body["items"]), 1)
        self.assertEqual(body["items"][0]["title"], "B")
        self.assertEqual(body["items"][0]["status"], "completed")

    def test_patch_task_idempotent_and_preserves_unspecified(self):
        status, _, created = self._request_json(
            "POST",
            "/tasks",
            {"title": "Patch me", "status": "pending", "dueDate": "2026-06-01T10:00:00Z"},
        )
        self.assertEqual(status, 201)
        task_id = created["id"]

        status, _, first_patch = self._request_json(
            "PATCH",
            f"/tasks/{task_id}",
            {"status": "completed"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(first_patch["status"], "completed")
        self.assertEqual(first_patch["title"], "Patch me")
        self.assertEqual(first_patch["dueDate"], "2026-06-01T10:00:00Z")

        status, _, second_patch = self._request_json(
            "PATCH",
            f"/tasks/{task_id}",
            {"status": "completed"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(second_patch["status"], "completed")
        self.assertEqual(second_patch["title"], "Patch me")
        self.assertEqual(second_patch["dueDate"], "2026-06-01T10:00:00Z")

    def test_patch_task_error_path_rfc7807(self):
        status, headers, body = self._request_json("PATCH", "/tasks/99999", {"status": "completed"})
        self.assertEqual(status, 404)
        self.assertEqual(headers.get("Content-Type"), "application/problem+json")
        self.assertEqual(body["status"], 404)
        self.assertEqual(body["title"], "Task not found")

    def test_delete_task_success(self):
        status, _, created = self._request_json("POST", "/tasks", {"title": "Delete me"})
        self.assertEqual(status, 201)
        task_id = created["id"]

        status, _, _ = self._request_json("DELETE", f"/tasks/{task_id}")
        self.assertEqual(status, 204)

    def test_delete_task_error_path_rfc7807(self):
        status, headers, body = self._request_json("DELETE", "/tasks/99999")
        self.assertEqual(status, 404)
        self.assertEqual(headers.get("Content-Type"), "application/problem+json")
        self.assertEqual(body["status"], 404)
        self.assertEqual(body["title"], "Task not found")


if __name__ == "__main__":
    unittest.main()
