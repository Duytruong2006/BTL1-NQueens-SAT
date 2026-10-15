"""N-Queens bằng CNF tự xây dựng và SAT solver thật của PySAT.

Biến ô (r, c) có ID r*n+c+1, với chỉ số bắt đầu từ 0. Mỗi hàng
và cột có đúng một hậu; mỗi đường chéo có nhiều nhất một hậu.
Không thêm ràng buộc phá đối xứng trong bất kỳ encoding nào.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from math import isqrt
from pathlib import Path
from time import perf_counter
from typing import Iterable, Sequence


ENCODINGS = ("pairwise", "binary", "sequential", "commander", "product")


@dataclass
class CNFFormula:
    """CNF với bộ cấp ID biến dùng chung cho toàn bàn cờ."""

    n: int
    encoding: str
    nvars: int
    primary: list[int]
    clauses: list[list[int]] = field(default_factory=list)

    def fresh(self, count: int = 1) -> list[int]:
        variables = list(range(self.nvars + 1, self.nvars + count + 1))
        self.nvars += count
        return variables

    def add(self, literals: Iterable[int]) -> None:
        self.clauses.append(list(literals))

    def write_dimacs(self, path: str | Path) -> None:
        """Xuất DIMACS CNF để có thể giải bằng solver bên ngoài."""
        with Path(path).open("w", encoding="ascii", newline="\n") as stream:
            stream.write(f"c N-Queens n={self.n} encoding={self.encoding}\n")
            stream.write(f"p cnf {self.nvars} {len(self.clauses)}\n")
            for clause in self.clauses:
                stream.write(" ".join(map(str, clause)) + " 0\n")


def _pairwise(xs: Sequence[int], cnf: CNFFormula) -> None:
    for i, x in enumerate(xs):
        for y in xs[i + 1:]:
            cnf.add((-x, -y))


def add_amo(xs: Sequence[int], cnf: CNFFormula, encoding: str) -> None:
    """Thêm AMO(xs), tương đương tồn tại các biến phụ của encoding.

    Caller truyền các ID dương, đôi một khác nhau, đã được cấp phát.
    AMO của tập rỗng hoặc một phần tử luôn đúng và không sinh mệnh đề.
    """
    if encoding not in ENCODINGS:
        raise ValueError(f"Unknown encoding: {encoding}; choose {ENCODINGS}")
    m = len(xs)
    if m <= 1:
        return
    if encoding == "pairwise":
        _pairwise(xs, cnf)
    elif encoding == "binary":
        bits = cnf.fresh((m - 1).bit_length())
        for index, x in enumerate(xs):
            for bit_index, bit in enumerate(bits):
                cnf.add((-x, bit if index & (1 << bit_index) else -bit))
    elif encoding == "sequential":
        # Bộ đếm Sinz cho k=1: m-1 biến phụ, 3m-4 mệnh đề.
        prefix = cnf.fresh(m - 1)
        cnf.add((-xs[0], prefix[0]))
        for i in range(1, m - 1):
            cnf.add((-xs[i], prefix[i]))
            cnf.add((-prefix[i - 1], prefix[i]))
            cnf.add((-xs[i], -prefix[i - 1]))
        cnf.add((-xs[-1], -prefix[-1]))
    elif encoding == "commander":
        if m <= 3:
            _pairwise(xs, cnf)
            return
        commanders = []
        for start in range(0, m, 3):
            group = xs[start:start + 3]
            commander = cnf.fresh()[0]
            commanders.append(commander)
            _pairwise(group, cnf)
            # commander <=> OR(group), kể cả nhóm cuối chỉ có 1-2 biến.
            for x in group:
                cnf.add((-x, commander))
            cnf.add([-commander, *group])
        add_amo(commanders, cnf, "commander")
    elif encoding == "product":
        if m <= 3:
            _pairwise(xs, cnf)
            return
        p = isqrt(m)
        if p * p < m:
            p += 1
        q = (m + p - 1) // p
        rows, columns = cnf.fresh(p), cnf.fresh(q)
        _pairwise(rows, cnf)
        _pairwise(columns, cnf)
        for index, x in enumerate(xs):
            cnf.add((-x, rows[index // q]))
            cnf.add((-x, columns[index % q]))


def amo_cnf(m: int, encoding: str) -> CNFFormula:
    """CNF của một ràng buộc AMO độc lập, hữu ích khi kiểm thử."""
    if isinstance(m, bool) or not isinstance(m, int) or m < 0:
        raise ValueError("m must be a nonnegative integer")
    cnf = CNFFormula(0, encoding, m, list(range(1, m + 1)))
    add_amo(cnf.primary, cnf, encoding)
    return cnf


def encode(n: int, encoding: str = "sequential") -> CNFFormula:
    """Dựng CNF N-Queens; n phải là số nguyên dương."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if encoding not in ENCODINGS:
        raise ValueError(f"Unknown encoding: {encoding}; choose {ENCODINGS}")
    cnf = CNFFormula(n, encoding, n * n, list(range(1, n * n + 1)))

    def cell(r: int, c: int) -> int:
        return r * n + c + 1

    for r in range(n):
        row = [cell(r, c) for c in range(n)]
        cnf.add(row)
        add_amo(row, cnf, encoding)
    for c in range(n):
        column = [cell(r, c) for r in range(n)]
        cnf.add(column)
        add_amo(column, cnf, encoding)
    for difference in range(1 - n, n):
        diagonal = [cell(r, r - difference) for r in range(n)
                    if 0 <= r - difference < n]
        add_amo(diagonal, cnf, encoding)
    for total in range(2 * n - 1):
        diagonal = [cell(r, total - r) for r in range(n)
                    if 0 <= total - r < n]
        add_amo(diagonal, cnf, encoding)
    return cnf


def validate_solution(n: int, columns: Sequence[int] | None) -> bool:
    """Kiểm tra trực tiếp bàn cờ, độc lập với CNF và SAT solver."""
    if (isinstance(n, bool) or not isinstance(n, int) or n < 1
            or columns is None or len(columns) != n):
        return False
    if any(isinstance(c, bool) or not isinstance(c, int) or not 0 <= c < n
           for c in columns):
        return False
    return (len(set(columns)) == n
            and len({r - c for r, c in enumerate(columns)}) == n
            and len({r + c for r, c in enumerate(columns)}) == n)


def decode_solution(n: int, model: Sequence[int]) -> list[int]:
    """Giải mã biến chính; từ chối mô hình không có đúng một hậu/hàng."""
    positive = {literal for literal in model if 0 < literal <= n * n}
    columns = []
    for r in range(n):
        selected = [c for c in range(n) if r * n + c + 1 in positive]
        if len(selected) != 1:
            raise RuntimeError(f"Invalid SAT model: row {r} has {len(selected)} queens")
        columns.append(selected[0])
    return columns


def solve(n: int, encoding: str = "sequential", solver: str = "g3") -> dict:
    """Đo thời gian, chạy PySAT và kiểm tra nghiệm trả về.

    Giới hạn thời gian cứng do chương trình benchmark quản lý bằng tiến trình
    con. Hàm này không giả lập solver và không biến timeout thành UNSAT.
    """
    from pysat.solvers import Solver

    start = perf_counter()
    cnf = encode(n, encoding)
    after_build = perf_counter()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as sat_solver:
        after_setup = perf_counter()
        satisfiable = sat_solver.solve()
        after_solve = perf_counter()
        model = sat_solver.get_model() if satisfiable else None
        solution = decode_solution(n, model) if model is not None else None
        verified = validate_solution(n, solution) if satisfiable else None
        if satisfiable and not verified:
            raise RuntimeError("SAT solver returned an invalid N-Queens solution")
        statistics = sat_solver.accum_stats()
    return {
        "n": n,
        "encoding": encoding,
        "solver": solver,
        "status": "SAT" if satisfiable else "UNSAT",
        "build_seconds": after_build - start,
        "solver_setup_seconds": after_setup - after_build,
        "solve_seconds": after_solve - after_setup,
        "total_seconds": perf_counter() - start,
        "nvars": cnf.nvars,
        "nprimary": n * n,
        "nauxiliary": cnf.nvars - n * n,
        "nclauses": len(cnf.clauses),
        "solution": solution,
        "verified": verified,
        "solver_stats": statistics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="N-Queens with five SAT encodings")
    parser.add_argument("n", type=int, help="Positive board size")
    parser.add_argument("--encoding", choices=ENCODINGS, default="sequential")
    parser.add_argument("--solver", default="g3", help="PySAT solver name (default: Glucose3)")
    parser.add_argument("--cnf", type=Path, help="Also export the encoded instance as DIMACS")
    parser.add_argument("--encode-only", action="store_true", help="Do not call a SAT solver")
    args = parser.parse_args()
    if args.cnf or args.encode_only:
        cnf = encode(args.n, args.encoding)
        if args.cnf:
            cnf.write_dimacs(args.cnf)
        if args.encode_only:
            print(json.dumps({"n": args.n, "encoding": args.encoding,
                              "nvars": cnf.nvars, "nclauses": len(cnf.clauses)}))
            return
    print(json.dumps(solve(args.n, args.encoding, args.solver), ensure_ascii=False))


if __name__ == "__main__":
    main()
