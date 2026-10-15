"""Exact comparison solvers for the decision version of N-Queens.

Public API: ``solve(n, backend, time_limit=30)``.  A solution stores one
zero-based column for every row.  SAT always requires independent validation;
UNSAT requires an explicit infeasibility proof reported by the solver.

Imports and availability checks are excluded from timing. ``build_seconds``
includes native model initialization, parameters and constraints;
``solve_seconds`` measures the blocking solver call, and ``total_seconds`` is
their sum. A missing phase is None, never a made-up zero. The time limit applies
to solver search, not Python model construction. Native presolve and symmetry
handling remain at defaults; no hand-written symmetry constraints are added.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import math
import os
from pathlib import Path
import shutil
import time
from numbers import Integral
from typing import Any


BACKENDS = ("cp_sat", "cplex_mip", "gurobi", "cplex_cp")
SEED = 42


def verify_solution(n: int, solution: Any) -> bool:
    """Validate board geometry without consulting any solver/model objects."""
    if not isinstance(solution, (list, tuple)) or len(solution) != n:
        return False
    if any(isinstance(c, bool) or not isinstance(c, Integral)
           or not 0 <= c < n for c in solution):
        return False
    return (len(set(solution)) == n
            and len({r + c for r, c in enumerate(solution)}) == n
            and len({r - c for r, c in enumerate(solution)}) == n)


def _version(distribution: str, module: Any) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return str(getattr(module, "__version__", "unknown"))


def _load(record: dict, module_name: str, distribution: str) -> Any:
    module = importlib.import_module(module_name)
    record["module"] = module_name
    record["version"] = _version(distribution, module)
    return module


def _begin_build(record: dict) -> None:
    record["_build_started"] = time.perf_counter()


def _begin_solve(record: dict) -> None:
    now = time.perf_counter()
    record["build_seconds"] = now - record.pop("_build_started")
    record["_solve_started"] = now


def _end_solve(record: dict) -> None:
    record["solve_seconds"] = time.perf_counter() - record.pop("_solve_started")
    record["total_seconds"] = record["build_seconds"] + record["solve_seconds"]


def _sat(record: dict, columns: list[int]) -> None:
    record["solution"] = columns
    record["verified"] = verify_solution(record["n"], columns)
    record["status"] = "SAT" if record["verified"] else "ERROR"
    record["message"] = ("Valid N-Queens solution independently verified."
                         if record["verified"] else
                         "Solver returned a board that failed independent validation.")


def _classify_exception(exc: Exception) -> str:
    """Keep license/installation failures distinct from mathematical results."""
    text = str(exc).lower()
    error_number = getattr(exc, "errno", None)
    if (error_number == 10010 or "1016" in text
            or "size-limited" in text or "size limited" in text
            or "community edition" in text or "problem size limits" in text):
        return "LICENSE_LIMIT"
    if (isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError))
            or error_number == 10009 or "license" in text or "licence" in text
            or "executable file is not found" in text
            or "cannot find executable" in text):
        return "UNAVAILABLE"
    return "ERROR"


def _diagonal_cells(n: int):
    """Yield both families of diagonals, omitting trivial singleton lines."""
    for delta in range(-(n - 2), n - 1):
        cells = [(r, r - delta) for r in range(max(0, delta), min(n, n + delta))]
        if len(cells) >= 2:
            yield cells
    for total in range(1, 2 * n - 2):
        cells = [(r, total - r)
                 for r in range(max(0, total - n + 1), min(n, total + 1))]
        if len(cells) >= 2:
            yield cells


def _solve_cp_sat(record: dict) -> None:
    cp = _load(record, "ortools.sat.python.cp_model", "ortools")
    n = record["n"]
    _begin_build(record)
    model = cp.CpModel()
    q = [model.NewIntVar(0, n - 1, f"q_{r}") for r in range(n)]
    model.AddAllDifferent(q)
    model.AddAllDifferent([q[r] + r for r in range(n)])
    model.AddAllDifferent([q[r] - r for r in range(n)])
    solver = cp.CpSolver()
    solver.parameters.max_time_in_seconds = record["time_limit"]
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = SEED
    solver.parameters.log_search_progress = False
    record["solver_version"] = record["version"]
    _begin_solve(record)
    status = solver.Solve(model)
    _end_solve(record)
    record["solver_status"] = solver.StatusName(status)
    if status in (cp.OPTIMAL, cp.FEASIBLE):
        _sat(record, [int(solver.Value(v)) for v in q])
    elif status == cp.INFEASIBLE:
        record.update(status="UNSAT", message="CP-SAT proved infeasibility.")
    elif status == cp.UNKNOWN:
        record.update(status="TIMEOUT", message="Search stopped without a solution or an infeasibility proof.")
    else:
        record.update(status="ERROR", message=f"Unexpected CP-SAT status: {record['solver_status']}")


def _solve_cplex_mip(record: dict) -> None:
    cp = _load(record, "cplex", "cplex")
    n = record["n"]
    model = None
    try:
        _begin_build(record)
        model = cp.Cplex()
        model.set_log_stream(None)
        model.set_results_stream(None)
        model.set_warning_stream(None)
        model.set_error_stream(None)
        record["solver_version"] = model.get_version()
        model.parameters.threads.set(1)
        model.parameters.randomseed.set(SEED)
        model.parameters.timelimit.set(record["time_limit"])
        model.variables.add(obj=[0.0] * (n * n),
                            types=[model.variables.type.binary] * (n * n))
        rows = [cp.SparsePair(ind=[r * n + c for c in range(n)], val=[1.0] * n)
                for r in range(n)]
        rows += [cp.SparsePair(ind=[r * n + c for r in range(n)], val=[1.0] * n)
                 for c in range(n)]
        senses = ["E"] * (2 * n)
        for cells in _diagonal_cells(n):
            rows.append(cp.SparsePair(ind=[r * n + c for r, c in cells],
                                      val=[1.0] * len(cells)))
            senses.append("L")
        model.linear_constraints.add(lin_expr=rows, senses=senses, rhs=[1.0] * len(rows))
        _begin_solve(record)
        model.solve()
        _end_solve(record)
        status = model.solution.get_status()
        record["solver_status"] = model.solution.get_status_string(status)
        if model.solution.is_primal_feasible():
            values = model.solution.get_values()
            columns = []
            for r in range(n):
                selected = [c for c in range(n) if values[r * n + c] > 0.5]
                columns.append(selected[0] if len(selected) == 1 else -1)
            _sat(record, columns)
        elif status == model.solution.status.MIP_infeasible:
            record.update(status="UNSAT", message="CPLEX MIP proved infeasibility.")
        elif status in (model.solution.status.MIP_time_limit_infeasible,
                        model.solution.status.MIP_dettime_limit_infeasible):
            record.update(status="TIMEOUT", message="CPLEX reached its time limit without a solution.")
        else:
            record.update(status="ERROR", message=f"CPLEX did not establish SAT or UNSAT: {record['solver_status']}")
    finally:
        if model is not None:
            model.end()


def _solve_gurobi(record: dict) -> None:
    gp = _load(record, "gurobipy", "gurobipy")
    n = record["n"]
    env = model = None
    try:
        _begin_build(record)
        env = gp.Env(empty=True)
        env.setParam("OutputFlag", 0)
        env.start()
        model = gp.Model("nqueens", env=env)
        record["solver_version"] = ".".join(str(v) for v in gp.gurobi.version())
        model.Params.Threads = 1
        model.Params.Seed = SEED
        model.Params.TimeLimit = record["time_limit"]
        x = model.addVars(n, n, vtype=gp.GRB.BINARY, name="x")
        model.addConstrs((gp.quicksum(x[r, c] for c in range(n)) == 1 for r in range(n)))
        model.addConstrs((gp.quicksum(x[r, c] for r in range(n)) == 1 for c in range(n)))
        for cells in _diagonal_cells(n):
            model.addConstr(gp.quicksum(x[r, c] for r, c in cells) <= 1)
        model.setObjective(0.0, gp.GRB.MINIMIZE)
        model.update()
        _begin_solve(record)
        model.optimize()
        _end_solve(record)
        status = model.Status
        status_names = {getattr(gp.GRB, name): name for name in (
            "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED", "TIME_LIMIT",
            "NODE_LIMIT", "ITERATION_LIMIT", "SOLUTION_LIMIT", "INTERRUPTED",
            "NUMERIC", "SUBOPTIMAL", "LOADED", "INPROGRESS", "USER_OBJ_LIMIT")
            if hasattr(gp.GRB, name)}
        record["solver_status"] = status_names.get(status, str(status))
        if model.SolCount > 0:
            columns = []
            for r in range(n):
                selected = [c for c in range(n) if x[r, c].X > 0.5]
                columns.append(selected[0] if len(selected) == 1 else -1)
            _sat(record, columns)
        elif status == gp.GRB.INFEASIBLE:
            record.update(status="UNSAT", message="Gurobi proved infeasibility.")
        elif status == gp.GRB.TIME_LIMIT:
            record.update(status="TIMEOUT", message="Gurobi reached its time limit without a solution.")
        else:
            record.update(status="ERROR", message=f"Gurobi did not establish SAT or UNSAT: {record['solver_status']}")
    finally:
        if model is not None:
            model.dispose()
        if env is not None:
            env.dispose()


def find_cpoptimizer() -> str | None:
    """Read-only local discovery; never contact a cloud service or buy a license."""
    for key in ("CPO_EXECUTABLE", "CP_OPTIMIZER_EXECUTABLE"):
        value = os.environ.get(key)
        if value and Path(value).is_file():
            return str(Path(value).resolve())
    found = shutil.which("cpoptimizer") or shutil.which("cpoptimizer.exe")
    if found:
        return found
    # Recent IBM pip distributions include the local CP Optimizer executable
    # next to the cplex package, including --target and virtual environments.
    spec = importlib.util.find_spec('cplex')
    if spec is not None and spec.origin:
        package_root = Path(spec.origin).resolve().parent.parent
        for candidate in (package_root / 'bin' / 'cpoptimizer.exe',
                          package_root / 'bin' / 'cpoptimizer'):
            if candidate.is_file():
                return str(candidate)
    roots = [Path(value) for key, value in os.environ.items()
             if key.upper().startswith("CPLEX_STUDIO_DIR") and value]
    for parent in (Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "IBM/ILOG",
                   Path("C:/IBM/ILOG"), Path("/opt/ibm/ILOG"),
                   Path("/Applications")):
        if parent.is_dir():
            roots.extend(sorted(parent.glob("CPLEX_Studio*")))
    for root in roots:
        for pattern in ("cpoptimizer/bin/*/cpoptimizer.exe", "cpoptimizer/bin/*/cpoptimizer"):
            for candidate in sorted(root.glob(pattern)):
                if candidate.is_file():
                    return str(candidate.resolve())
    return None


def _solve_cplex_cp(record: dict) -> None:
    cp = _load(record, "docplex.cp.model", "docplex")
    executable = find_cpoptimizer()
    record["executable"] = executable
    if executable is None:
        record.update(status="UNAVAILABLE", message=(
            "docplex is installed but the local IBM CP Optimizer executable was not found. "
            "Install a licensed IBM ILOG CPLEX Optimization Studio and set CPO_EXECUTABLE "
            "to its cpoptimizer executable. CPLEX MIP and OR-Tools CP-SAT are different solvers."))
        return
    n = record["n"]
    _begin_build(record)
    model = cp.CpoModel(name="nqueens")
    q = model.integer_var_list(n, min=0, max=n - 1, name="q")
    model.add(model.all_diff(q))
    model.add(model.all_diff([q[r] + r for r in range(n)]))
    model.add(model.all_diff([q[r] - r for r in range(n)]))
    _begin_solve(record)
    answer = model.solve(agent="local", execfile=executable,
                         TimeLimit=record["time_limit"], Workers=1,
                         RandomSeed=SEED, LogVerbosity="Quiet", trace_log=False)
    _end_solve(record)
    status = answer.get_solve_status()
    record["solver_status"] = str(status)
    record["search_status"] = str(answer.get_search_status())
    record["stop_cause"] = str(answer.get_stop_cause())
    native_version = answer.get_process_infos().get_solver_version()
    record["solver_version"] = str(native_version) if native_version is not None else "unknown"
    if answer.is_solution():
        _sat(record, [int(answer.get_value(v)) for v in q])
    elif str(status).lower() == "infeasible":
        record.update(status="UNSAT", message="IBM CP Optimizer proved infeasibility.")
    elif "limit" in record["stop_cause"].lower():
        record.update(status="TIMEOUT", message="IBM CP Optimizer reached a search limit without a solution.")
    else:
        record.update(status="ERROR", message=f"IBM CP Optimizer did not establish SAT or UNSAT: {status}")


def solve(n: int, backend: str, time_limit: float = 30) -> dict:
    """Run an exact backend and return a JSON-serializable measurement record.

    Supported statuses: SAT, UNSAT, TIMEOUT, UNAVAILABLE, LICENSE_LIMIT, ERROR.
    Invalid arguments are recorded as ERROR. ``verified`` means an actual SAT
    board was independently checked; it is False for UNSAT and unavailable runs.
    """
    record = dict(n=n, backend=backend, status="ERROR", build_seconds=None,
                  solve_seconds=None, total_seconds=None, solution=None,
                  verified=False, message="", module=None, version=None,
                  solver_version=None, solver_status=None, time_limit=time_limit,
                  threads=1, seed=SEED)
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 1:
        record["message"] = "n must be a positive integer."
        return record
    record["n"] = int(n)
    try:
        limit = float(time_limit)
    except (TypeError, ValueError):
        record["message"] = "time_limit must be a finite positive number."
        return record
    if isinstance(time_limit, bool) or not math.isfinite(limit) or limit <= 0:
        record["message"] = "time_limit must be a finite positive number."
        return record
    record["time_limit"] = limit
    handlers = dict(cp_sat=_solve_cp_sat, cplex_mip=_solve_cplex_mip,
                    gurobi=_solve_gurobi, cplex_cp=_solve_cplex_cp)
    if backend not in handlers:
        record["message"] = f"Unknown backend {backend!r}; expected one of {BACKENDS}."
        return record
    try:
        handlers[backend](record)
    except Exception as exc:
        # Failed search attempts have measured duration but are never successful
        # solve samples. Failed model construction has no completed build time.
        if "_solve_started" in record:
            _end_solve(record)
        record.update(status=_classify_exception(exc),
                      message=f"{type(exc).__name__}: {exc}")
    finally:
        record.pop("_build_started", None)
        record.pop("_solve_started", None)
    return record
