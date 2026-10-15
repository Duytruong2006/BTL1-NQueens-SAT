"""Meaningful geometry, status and optional real-solver integration checks."""

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import comparisons


class ComparisonTests(unittest.TestCase):
    def test_independent_geometry_validator(self):
        self.assertTrue(comparisons.verify_solution(1, [0]))
        self.assertTrue(comparisons.verify_solution(4, [1, 3, 0, 2]))
        for invalid in ([0, 1, 2, 3], [1, 3, 0, 1], [1, 3, 0, 4], [1, 3, 0],
                        [True, 3, 0, 2], [1.0, 3, 0, 2]):
            self.assertFalse(comparisons.verify_solution(4, invalid))

    def test_all_and_only_nontrivial_diagonals_are_generated(self):
        for n in (1, 2, 4, 8):
            diagonals = list(comparisons._diagonal_cells(n))
            actual = set()
            for diagonal in diagonals:
                for i, left in enumerate(diagonal):
                    for right in diagonal[i + 1:]:
                        actual.add(tuple(sorted((left, right))))
            expected = set()
            cells = [(r, c) for r in range(n) for c in range(n)]
            for i, left in enumerate(cells):
                for right in cells[i + 1:]:
                    if abs(left[0] - right[0]) == abs(left[1] - right[1]):
                        expected.add(tuple(sorted((left, right))))
            self.assertEqual(actual, expected)

    def test_missing_dependency_is_not_a_timeout_or_zero_time(self):
        with patch.object(comparisons.importlib, "import_module",
                          side_effect=ModuleNotFoundError("missing dependency")):
            result = comparisons.solve(8, "cp_sat")
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertIsNone(result["total_seconds"])
        self.assertIsNone(result["solution"])
        self.assertFalse(result["verified"])

    def test_missing_cp_optimizer_is_explicit(self):
        if importlib.util.find_spec("docplex") is None:
            self.skipTest("docplex not installed")
        with patch.object(comparisons, "find_cpoptimizer", return_value=None):
            result = comparisons.solve(8, "cplex_cp")
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertIsNone(result["build_seconds"])
        self.assertIsNone(result["solve_seconds"])
        self.assertIsNone(result["total_seconds"])

    def test_license_errors_are_distinguished(self):
        self.assertEqual(comparisons._classify_exception(
            RuntimeError("CPLEX Error 1016: Community Edition. Problem size limits exceeded.")),
            "LICENSE_LIMIT")
        self.assertEqual(comparisons._classify_exception(
            RuntimeError("Model too large for size-limited license")), "LICENSE_LIMIT")
        self.assertEqual(comparisons._classify_exception(
            RuntimeError("No valid license found")), "UNAVAILABLE")

    def test_invalid_arguments(self):
        for n in (0, -1, 1.5, True):
            self.assertEqual(comparisons.solve(n, "cp_sat")["status"], "ERROR")
        for limit in (0, -1, float("inf"), float("nan"), True):
            self.assertEqual(comparisons.solve(4, "cp_sat", limit)["status"], "ERROR")
        self.assertEqual(comparisons.solve(4, "unsupported")["status"], "ERROR")

    def test_real_small_instances_all_available_backends(self):
        checked = 0
        for backend in comparisons.BACKENDS:
            first = comparisons.solve(1, backend, time_limit=10)
            if first["status"] in ("UNAVAILABLE", "LICENSE_LIMIT"):
                continue
            checked += 1
            for n in (1, 2, 3, 4, 8):
                with self.subTest(backend=backend, n=n):
                    result = first if n == 1 else comparisons.solve(n, backend, time_limit=10)
                    self.assertEqual(result["status"], "UNSAT" if n in (2, 3) else "SAT", result)
                    self.assertEqual(result["verified"], n not in (2, 3))
                    if n not in (2, 3):
                        self.assertTrue(comparisons.verify_solution(n, result["solution"]))
                    self.assertGreaterEqual(result["build_seconds"], 0)
                    self.assertGreaterEqual(result["solve_seconds"], 0)
                    self.assertAlmostEqual(result["total_seconds"],
                                           result["build_seconds"] + result["solve_seconds"])
                    self.assertIsNotNone(result["module"])
                    self.assertIsNotNone(result["version"])
        if not checked:
            self.skipTest("No exact solver backend is locally available")


if __name__ == "__main__":
    unittest.main()
