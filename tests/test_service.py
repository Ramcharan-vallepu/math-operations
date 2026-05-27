import logging
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from math_operations.errors import ArithmeticError, ValidationError
from math_operations.service import calculate


class TestMathService(unittest.TestCase):
    def test_addition(self):
        result = calculate("add", 10, 5)
        self.assertEqual(result["result"], 15)

    def test_subtraction(self):
        result = calculate("subtract", 10, 5)
        self.assertEqual(result["result"], 5)

    def test_multiplication(self):
        result = calculate("multiply", 10, 5)
        self.assertEqual(result["result"], 50)

    def test_division(self):
        result = calculate("divide", 10, 5)
        self.assertEqual(result["result"], 2)

    def test_modulus(self):
        result = calculate("modulus", 10, 3)
        self.assertEqual(result["result"], 1)

    def test_power(self):
        result = calculate("power", 2, 3)
        self.assertEqual(result["result"], 8)

    def test_divide_by_zero(self):
        with self.assertRaises(ArithmeticError) as ctx:
            calculate("divide", 10, 0)
        self.assertEqual(ctx.exception.code, "divide_by_zero")

    def test_invalid_input_type(self):
        with self.assertRaises(ValidationError):
            calculate("add", "abc", 2)

    def test_invalid_operation(self):
        with self.assertRaises(ValidationError) as ctx:
            calculate("sqrt", 4, 2)
        self.assertEqual(ctx.exception.code, "unsupported_operation")

    def test_logging_for_failed_operations(self):
        logger = logging.getLogger("math_operations")
        with self.assertLogs(logger=logger, level="ERROR") as logs:
            try:
                calculate("divide", 10, 0)
            except ArithmeticError:
                logger.error("Math operation request failed", extra={"code": "divide_by_zero"})
        self.assertTrue(any("Math operation request failed" in line for line in logs.output))

    def test_response_time_within_limit(self):
        started = time.perf_counter()
        calculate("power", 25, 2)
        elapsed_ms = (time.perf_counter() - started) * 1000
        self.assertLess(elapsed_ms, 100)


if __name__ == "__main__":
    unittest.main()
