"""Kiểm thử ngữ nghĩa encoding, nghiệm nhỏ và số nghiệm N-Queens."""

from itertools import product
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pysat.formula import CNF
from pysat.solvers import Solver

from nqueens_sat import (ENCODINGS, amo_cnf, decode_solution, encode, solve,
                         validate_solution)


class TestAMO(unittest.TestCase):
    def test_every_primary_assignment_with_existential_auxiliaries(self):
        """2^m cách gán biến chính; solver chọn tồn tại biến phụ, m=0..8."""
        cases = 0
        for encoding in ENCODINGS:
            for m in range(9):
                cnf = amo_cnf(m, encoding)
                with Solver(name="g3", bootstrap_with=cnf.clauses) as solver:
                    for values in product((False, True), repeat=m):
                        assumptions = [i + 1 if value else -(i + 1)
                                       for i, value in enumerate(values)]
                        with self.subTest(encoding=encoding, m=m, values=values):
                            self.assertEqual(solver.solve(assumptions=assumptions),
                                             sum(values) <= 1)
                        cases += 1
        self.assertEqual(cases, 5 * (2 ** 9 - 1))

    def test_sequential_clause_and_variable_counts(self):
        for m in range(2, 30):
            cnf = amo_cnf(m, "sequential")
            self.assertEqual(cnf.nvars - m, m - 1)
            self.assertEqual(len(cnf.clauses), 3 * m - 4)

    def test_binary_clause_and_variable_counts(self):
        for m in range(2, 30):
            cnf = amo_cnf(m, "binary")
            bits = (m - 1).bit_length()
            self.assertEqual(cnf.nvars - m, bits)
            self.assertEqual(len(cnf.clauses), m * bits)


class TestNQueens(unittest.TestCase):
    def test_small_boards(self):
        for encoding in ENCODINGS:
            for n in range(1, 13):
                with self.subTest(encoding=encoding, n=n):
                    result = solve(n, encoding)
                    expected = "UNSAT" if n in (2, 3) else "SAT"
                    self.assertEqual(result["status"], expected)
                    if expected == "SAT":
                        self.assertTrue(result["verified"])
                        self.assertTrue(validate_solution(n, result["solution"]))
                    else:
                        self.assertIsNone(result["solution"])
                        self.assertIsNone(result["verified"])

    def test_solution_counts_without_duplicate_auxiliary_assignments(self):
        expected_counts = (1, 0, 0, 2, 10, 4, 40, 92)
        for encoding in ENCODINGS:
            for n, expected in enumerate(expected_counts, start=1):
                cnf = encode(n, encoding)
                count = 0
                solutions = set()
                with Solver(name="g3", bootstrap_with=cnf.clauses) as solver:
                    while solver.solve():
                        columns = decode_solution(n, solver.get_model())
                        self.assertTrue(validate_solution(n, columns))
                        self.assertNotIn(tuple(columns), solutions)
                        solutions.add(tuple(columns))
                        count += 1
                        # Chặn bàn cờ, không chặn các cách gán biến phụ.
                        solver.add_clause([-(r * n + c + 1)
                                           for r, c in enumerate(columns)])
                with self.subTest(encoding=encoding, n=n):
                    self.assertEqual(count, expected)

    def test_validator_rejects_invalid_boards(self):
        self.assertTrue(validate_solution(4, [1, 3, 0, 2]))
        for columns in (None, [], [1, 3, 0], [1, 3, 0, 4], [0, 1, 2, 3],
                        [1, 1, 0, 2], [1, 3, 0, True]):
            self.assertFalse(validate_solution(4, columns))

    def test_invalid_parameters(self):
        for n in (0, -1, 2.5, True):
            with self.assertRaises(ValueError):
                encode(n)
        with self.assertRaises(ValueError):
            encode(4, "unknown")

    def test_dimacs_round_trip(self):
        cnf = encode(8, "commander")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queens.cnf"
            cnf.write_dimacs(path)
            parsed = CNF(from_file=str(path))
            self.assertEqual(parsed.nv, cnf.nvars)
            self.assertEqual(parsed.clauses, cnf.clauses)


if __name__ == "__main__":
    unittest.main(verbosity=2)
