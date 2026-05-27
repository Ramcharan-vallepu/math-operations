import json
import os
import sys
import threading
import unittest
from urllib import request
from urllib.error import HTTPError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from math_operations.api import create_server


class TestMathAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0)
        cls.host, cls.port = cls.server.server_address
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _post(self, payload):
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"http://{self.host}:{self.port}/calculate",
            method="POST",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with request.urlopen(req) as response:
                return response.getcode(), json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            return err.code, json.loads(err.read().decode("utf-8"))

    def test_calculate_success(self):
        status, body = self._post({"operation": "multiply", "a": 7, "b": 6})
        self.assertEqual(status, 200)
        self.assertEqual(body["result"], 42)

    def test_calculate_invalid_input(self):
        status, body = self._post({"operation": "add", "a": "bad", "b": 2})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "invalid_number")

    def test_divide_by_zero_error(self):
        status, body = self._post({"operation": "divide", "a": 8, "b": 0})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "divide_by_zero")


if __name__ == "__main__":
    unittest.main()
