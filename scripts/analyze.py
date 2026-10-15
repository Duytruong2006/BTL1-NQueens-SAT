"""Analyze recorded experiments only; no solver calls or invented samples.

Run again after raw.jsonl files finish growing. The summary never replaces a
timeout with its time limit. Figures use completed 3/3 SAT medians for the main
experiment; timeout triangles show a censoring boundary, not a solved runtime.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nqueens_sat import ENCODINGS, encode, validate_solution

MAIN_N = (8, 16, 32, 64, 128)
LARGE_N = (256, 512, 1000)
BACKENDS = ("cp_sat", "cplex_mip", "gurobi", "cplex_cp")
METHODS = tuple(ENCODINGS) + BACKENDS
LABELS = dict(pairwise="Pairwise", binary="Binary", sequential="Sequential",
              commander="Commander", product="Product", cp_sat="CP-SAT",
              cplex_mip="CPLEX MIP", gurobi="Gurobi", cplex_cp="CP Optimizer")
COLORS = ("#28587B", "#D17827", "#208477", "#8060A6", "#B74969")


def finite_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def read_raw(results_dir):
    records, sources, warnings, protocols = [], [], [], []
    for path in sorted(results_dir.glob("*/raw.jsonl")):
        protocol_path = path.with_name("protocol.json")
        protocol = json.loads(protocol_path.read_text(encoding="utf-8")) if protocol_path.exists() else {}
        folder = path.parent.name
        suite = protocol.get("suite") or ("large" if "large" in folder else
                                         "smoke" if "smoke" in folder else "main")
        if protocol:
            protocols.append(dict(source_directory=folder, **protocol))
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        accepted = 0
        for index, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                if index == len(lines) and not raw.endswith("\n"):
                    warnings.append(f"Incomplete final line ignored: {path}:{index}")
                    continue
                raise ValueError(f"Malformed JSON at {path}:{index}")
            if not isinstance(record, dict) or not all(key in record for key in ("method", "n", "repeat", "status")):
                raise ValueError(f"Missing record identity/status at {path}:{index}")
            if record["status"] == "SAT":
                if not record.get("verified") or not validate_solution(record["n"], record.get("solution")):
                    raise ValueError(f"Invalid or unverified SAT board at {path}:{index}")
                if not finite_number(record.get("elapsed_seconds")):
                    raise ValueError(f"Invalid SAT elapsed_seconds at {path}:{index}")
            records.append(dict(record, suite=suite, source_file=str(path.relative_to(ROOT)), source_line=index))
            accepted += 1
        sources.append(dict(file=str(path.relative_to(ROOT)), suite=suite,
                            lines_read=len(lines), records_read=accepted, bytes_read=len(raw.encode("utf-8"))))
    # Re-runs must not count the same trial twice. Preserve the latest recorded
    # timestamp and keep a warning if repeated trial identities exist.
    unique = {}
    for record in sorted(records, key=lambda item: item.get("timestamp", "")):
        key = (record["suite"], record["method"], record["n"], record["repeat"])
        if key in unique:
            warnings.append(f"Duplicate trial {key}: kept latest timestamp")
        unique[key] = record
    return list(unique.values()), sources, protocols, warnings


def summarize(records):
    buckets = defaultdict(list)
    for record in records:
        buckets[(record["suite"], record["method"], record["n"])].append(record)
    groups, status_rows = [], []
    for (suite, method, n), trials in sorted(buckets.items()):
        trials.sort(key=lambda record: record["repeat"])
        successes = [record for record in trials if record["status"] == "SAT"]
        times = [record["elapsed_seconds"] for record in successes]
        target = 3 if suite == "main" else 1
        status_counts = dict(sorted(Counter(record["status"] for record in trials).items()))
        group = dict(suite=suite, method=method, n=n, solved_count=len(successes),
                     trials=len(trials), expected_trials=target, status_counts=status_counts,
                     repeat_ids=[record["repeat"] for record in trials],
                     median_seconds=statistics.median(times) if times else None,
                     min_seconds=min(times) if times else None,
                     max_seconds=max(times) if times else None,
                     all_expected_trials_sat=(len(trials) == target and len(successes) == target
                                              and set(record["repeat"] for record in trials) == set(range(1, target + 1))))
        for source, output in (("build_seconds", "median_build_seconds"),
                               ("solver_setup_seconds", "median_setup_seconds"),
                               ("solve_seconds", "median_solve_seconds")):
            values = [record[source] for record in successes if finite_number(record.get(source))]
            group[output] = statistics.median(values) if len(values) == len(successes) and values else None
        group["timeout_limits"] = sorted({record["limit_seconds"] for record in trials
                                         if record["status"] == "TIMEOUT" and finite_number(record.get("limit_seconds"))})
        group["messages"] = sorted({record["message"] for record in trials if record.get("message")})
        groups.append(group)
        for status, count in status_counts.items():
            status_rows.append(dict(suite=suite, method=method, n=n, status=status,
                                    status_count=count, solved_count=len(successes), trials=len(trials),
                                    expected_trials=target,
                                    median_seconds=group["median_seconds"] if status == "SAT" else None,
                                    min_seconds=group["min_seconds"] if status == "SAT" else None,
                                    max_seconds=group["max_seconds"] if status == "SAT" else None,
                                    median_build_seconds=group["median_build_seconds"] if status == "SAT" else None,
                                    median_setup_seconds=group["median_setup_seconds"] if status == "SAT" else None,
                                    median_solve_seconds=group["median_solve_seconds"] if status == "SAT" else None))
    return groups, status_rows


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def cnf_counts():
    counts = []
    for n in (8, 32, 128):
        for method in ENCODINGS:
            cnf = encode(n, method)
            counts.append(dict(n=n, method=method, nvars=cnf.nvars,
                               nprimary=n * n, nauxiliary=cnf.nvars - n * n,
                               nclauses=len(cnf.clauses)))
            del cnf
    return counts


def number(value):
    if value is None:
        return "--"
    if value < 0.01:
        return f"{value:.6f}"
    if value < 1:
        return f"{value:.5f}"
    return f"{value:.3f}"


def table_cell(group):
    if group is None:
        return "--"
    if group["all_expected_trials_sat"]:
        return number(group["median_seconds"])
    if group["trials"] < group["expected_trials"]:
        return f"Pending ({group['trials']}/{group['expected_trials']})"
    codes = {"SAT": "SAT", "TIMEOUT": "TO", "UNAVAILABLE": "UNAV",
             "LICENSE_LIMIT": "LIC", "STARTUP_ERROR": "START", "STARTUP_TIMEOUT": "STO",
             "SKIPPED_RESOURCE": "SKIP", "ERROR": "ERR", "UNSAT": "UNSAT"}
    return "; ".join(f"{count} {codes.get(status, status)}" for status, count in group["status_counts"].items())


def tabular(headers, rows, alignment):
    body = [r"\begin{tabular}{" + alignment + "}", r"\toprule",
            " & ".join(headers) + r" \\", r"\midrule"]
    body.extend(" & ".join(str(cell) for cell in row) + r" \\" for row in rows)
    body.extend((r"\bottomrule", r"\end{tabular}", ""))
    return "\n".join(body)


def write_tables(groups, destination):
    lookup = {(g["suite"], g["method"], g["n"]): g for g in groups}
    rows = [[n] + [table_cell(lookup.get(("main", method, n))) for method in ENCODINGS] for n in MAIN_N]
    (destination / "main_sat_table.tex").write_text(
        tabular([r"$N$"] + [LABELS[m] for m in ENCODINGS], rows, "r" + "r" * 5), encoding="utf-8")
    rows = []
    for n in MAIN_N:
        eligible = [lookup[("main", method, n)] for method in ENCODINGS
                    if ("main", method, n) in lookup and lookup[("main", method, n)]["all_expected_trials_sat"]]
        best = min((g["median_seconds"] for g in eligible), default=None)
        rows.append([n, number(best)] + [table_cell(lookup.get(("main", method, n))) for method in BACKENDS])
    (destination / "comparison_table.tex").write_text(
        tabular([r"$N$", "Best SAT"] + [LABELS[m] for m in BACKENDS], rows, "r" + "r" * 5), encoding="utf-8")
    rows = [[LABELS[method]] + [table_cell(lookup.get(("large", method, n))) for n in LARGE_N] for method in METHODS]
    (destination / "large_table.tex").write_text(
        tabular(["Method"] + [str(n) for n in LARGE_N], rows, "lrrr"), encoding="utf-8")


def create_figures(groups, counts, records, destination):
    config_dir = ROOT.parent / "tmp" / "mpl_config"
    config_dir.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(config_dir)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle
    from matplotlib.colors import ListedColormap
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "pdf.fonttype": 42})
    lookup = {(g["suite"], g["method"], g["n"]): g for g in groups}

    def save(figure, name):
        figure.savefig(destination / f"{name}.pdf", bbox_inches="tight")
        figure.savefig(destination / f"{name}.png", dpi=180, bbox_inches="tight")
        plt.close(figure)

    fig, ax = plt.subplots(figsize=(7.5, 4.4), layout="constrained")
    has_timeout = False
    boundaries = set()
    for index, (method, color) in enumerate(zip(ENCODINGS, COLORS)):
        values = []
        for n in MAIN_N:
            group = lookup.get(("main", method, n))
            values.append(group["median_seconds"] if group and group["all_expected_trials_sat"] else float("nan"))
            if group and group["timeout_limits"]:
                has_timeout = True
                for limit in group["timeout_limits"]:
                    boundaries.add(limit)
                    # Small horizontal offsets keep coincident timeout markers readable.
                    ax.scatter(n * 2 ** ((index - 2) * .018), limit, marker="^", s=72,
                               facecolors="none", edgecolors=color, linewidths=1.6, zorder=5)
        ax.plot(MAIN_N, values, color=color, marker="o", markersize=4.5, linewidth=1.6, label=LABELS[method])
    for limit in boundaries:
        ax.axhline(limit, color="#888888", linestyle="--", linewidth=.8)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(MAIN_N, labels=[str(n) for n in MAIN_N])
    ax.set_xlabel("Board size N")
    ax.set_ylabel("End-to-end time (seconds, log scale)")
    ax.set_title("N-Queens SAT encodings | Glucose3")
    ax.grid(axis="y", which="major", alpha=.18)
    handles, labels = ax.get_legend_handles_labels()
    if has_timeout:
        handles.append(Line2D([], [], color="#555555", marker="^", markerfacecolor="none", linestyle="None"))
        labels.append("Timeout boundary (censored)")
    ax.legend(handles, labels, fontsize=8, loc="best", frameon=False)
    fig.text(.5, -.02, "Circles: median of 3/3 SAT runs. Missing circles are not solved-time estimates.",
             ha="center", fontsize=8, color="#555555")
    save(fig, "runtime")

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), layout="constrained")
    for method, color in zip(ENCODINGS, COLORS):
        rows = sorted((row for row in counts if row["method"] == method), key=lambda row: row["n"])
        for ax, field in zip(axes, ("nclauses", "nvars")):
            ax.plot([row["n"] for row in rows], [row[field] for row in rows],
                    marker="o", linewidth=1.5, color=color, label=LABELS[method])
    for ax, label in zip(axes, ("CNF clauses", "Boolean variables (total)")):
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks((8, 32, 128), labels=("8", "32", "128"))
        ax.set_xlabel("Board size N")
        ax.set_ylabel(label)
        ax.grid(axis="y", which="major", alpha=.18)
    axes[0].legend(fontsize=7, frameon=False)
    save(fig, "clauses")

    candidates = [record for record in records if record["n"] == 8 and record["status"] == "SAT"]
    if not candidates:
        return None
    board = min(candidates, key=lambda record: (record["method"] != "sequential", record["repeat"], record["method"]))
    solution = board["solution"]
    fig, ax = plt.subplots(figsize=(4.4, 4.4), layout="constrained")
    ax.imshow([[(r + c) % 2 for c in range(8)] for r in range(8)],
              cmap=ListedColormap(["#F3EEE4", "#C1B6A3"]), vmin=0, vmax=1)
    for r, c in enumerate(solution):
        ax.add_patch(Circle((c, r), .32, facecolor="#28587B", edgecolor="white", linewidth=1))
        ax.text(c, r, "Q", ha="center", va="center", color="white", fontweight="bold", fontsize=13)
    ax.set_xticks(range(8))
    ax.set_yticks(range(8))
    ax.set_xlabel("Column (zero-based)")
    ax.set_ylabel("Row (zero-based)")
    ax.set_title(f"Verified N=8 solution | {LABELS.get(board['method'], board['method'])}", fontsize=10)
    save(fig, "example_board")
    return {key: board[key] for key in ("n", "method", "repeat", "solution", "source_file", "source_line")}


def findings(groups, counts):
    lookup = {(g["suite"], g["method"], g["n"]): g for g in groups}
    fastest, speedups = [], []
    for n in MAIN_N:
        eligible = [lookup[("main", method, n)] for method in ENCODINGS
                    if ("main", method, n) in lookup and lookup[("main", method, n)]["all_expected_trials_sat"]]
        if eligible:
            winner = min(eligible, key=lambda g: g["median_seconds"])
            fastest.append(dict(n=n, method=winner["method"], median_seconds=winner["median_seconds"],
                                eligible_methods=[g["method"] for g in eligible],
                                all_five_eligible=len(eligible) == len(ENCODINGS)))
        baseline = lookup.get(("main", "pairwise", n))
        if baseline and baseline["all_expected_trials_sat"]:
            for group in eligible:
                if group["method"] != "pairwise" and group["median_seconds"] > 0:
                    speedups.append(dict(n=n, method=group["method"],
                                         pairwise_median_seconds=baseline["median_seconds"],
                                         method_median_seconds=group["median_seconds"],
                                         speedup=baseline["median_seconds"] / group["median_seconds"]))
    baseline_count = next(row["nclauses"] for row in counts if row["n"] == 128 and row["method"] == "pairwise")
    reductions = [dict(method=row["method"], n=128, nclauses=row["nclauses"],
                       pairwise_nclauses=baseline_count,
                       reduction_percent=100 * (1 - row["nclauses"] / baseline_count))
                  for row in counts if row["n"] == 128 and row["method"] != "pairwise"]
    return dict(fastest_sat_methods_by_n=fastest, speedups_vs_pairwise=speedups,
                clause_reductions_at_128=reductions,
                non_success_groups=[g for g in groups if set(g["status_counts"]) != {"SAT"}],
                main_sat_complete=all(lookup.get(("main", method, n), {}).get("trials") == 3
                                      for method in ENCODINGS for n in MAIN_N))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    parser.add_argument("--generated", type=Path, default=ROOT / "report" / "generated")
    parser.add_argument("--figures", type=Path, default=ROOT / "report" / "generated")
    args = parser.parse_args()
    for directory in (args.results, args.generated, args.figures):
        directory.mkdir(parents=True, exist_ok=True)
    records, sources, protocols, warnings = read_raw(args.results)
    if not records:
        raise SystemExit("No recorded trials found; no figures or samples were invented.")
    groups, status_rows = summarize(records)
    write_csv(args.results / "summary.csv", status_rows)
    counts = cnf_counts()
    write_csv(args.results / "cnf_counts.csv", counts)
    write_tables(groups, args.generated)
    board = create_figures(groups, counts, records, args.figures)
    if board is None:
        warnings.append("No verified N=8 result found; example_board was not generated.")
    analysis = dict(created_at=datetime.now(timezone.utc).isoformat(),
                    timing_metric="elapsed_seconds: build + solver setup + search + decode + validation; imports excluded",
                    statistical_policy="Only verified SAT records enter medians/min/max. TIMEOUT is right-censored; its limit is never a solved runtime. Main charts/tables show medians only for complete 3/3 SAT groups.",
                    table_legend={"TO": "Work timeout", "LIC": "License size limit", "UNAV": "Unavailable solver",
                                  "START": "Startup failure; inspect startup_reason and raw message",
                                  "STO": "Startup timeout", "SKIP": "Predeclared resource cap", "ERR": "Error",
                                  "--": "No recorded trial", "Pending": "Incomplete set of expected repeats"},
                    source_scope=sources, protocols=protocols, records_analyzed=len(records),
                    groups=groups, cnf_counts=counts, example_board=board,
                    findings=findings(groups, counts), warnings=warnings)
    (args.results / "analysis.json").write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(dict(records_analyzed=len(records), groups=len(groups),
                          summary=str(args.results / "summary.csv"), analysis=str(args.results / "analysis.json"),
                          warnings=warnings), ensure_ascii=False))


if __name__ == "__main__":
    main()
