"""Run isolated, serial benchmarks and preserve raw results (no fabricated times)."""
from __future__ import annotations
import argparse, csv, importlib.metadata, json, math, os, platform, random
import queue, signal, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
ENCODINGS = ['pairwise', 'binary', 'sequential', 'commander', 'product']
BACKENDS = ['cp_sat', 'cplex_mip', 'gurobi', 'cplex_cp']

def environment():
    packages = {}
    for name in ['python-sat','ortools','cplex','gurobipy','docplex']:
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
    cpu = platform.processor()
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    except (ImportError, OSError): pass
    memory = None
    try:
        import psutil
        memory = psutil.virtual_memory().total
    except ImportError: pass
    if memory is None and os.name == 'nt':
        import ctypes
        class MemoryStatus(ctypes.Structure):
            _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[
                (name,ctypes.c_ulonglong) for name in ('total_phys','avail_phys',
                'total_page','avail_page','total_virtual','avail_virtual','avail_extended')]
        status=MemoryStatus(); status.length=ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            memory=status.total_phys
    return dict(created_at=datetime.now(timezone.utc).isoformat(), python=sys.version,
                os=platform.platform(), cpu=cpu, logical_processors=os.cpu_count(),
                memory_bytes=memory, packages=packages)

def worker(args):
    # Load imports before READY; the parent arms the deadline before GO.
    try:
        if args.method in ENCODINGS:
            import pysat.solvers
            from nqueens_sat import solve
        elif args.method in BACKENDS:
            from comparisons import solve
            if args.method == 'cp_sat': from ortools.sat.python import cp_model
            elif args.method == 'gurobi': import gurobipy
            elif args.method == 'cplex_mip': import cplex
            elif args.method == 'cplex_cp':
                import docplex.cp.model
                import docplex.cp.solver.solver
                import docplex.cp.solver.solver_local
        else:
            raise ValueError(f'Unknown method: {args.method}')
    except Exception as exc:
        print('STARTUP_ERROR ' + json.dumps(dict(
            status='STARTUP_ERROR', phase='startup', elapsed_seconds=None,
            startup_reason='UNAVAILABLE' if isinstance(exc, ImportError) else 'ERROR',
            message=f'{type(exc).__name__}: {exc}')), flush=True)
        return
    print('READY', flush=True)
    if sys.stdin.readline().strip() != 'GO':
        return
    start = time.perf_counter()
    try:
        result = (solve(args.n,args.method) if args.method in ENCODINGS
                  else solve(args.n,args.method,time_limit=args.limit))
    except Exception as exc:
        result = dict(status='ERROR', message=f'{type(exc).__name__}: {exc}')
    result['elapsed_seconds'] = time.perf_counter()-start
    print('RESULT ' + json.dumps(result, ensure_ascii=True), flush=True)


def _kill_process_tree(proc):
    """Kill this worker and external solver children such as CP Optimizer."""
    if proc.poll() is not None:
        return
    if os.name == 'nt':
        try:
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
        except (OSError, subprocess.TimeoutExpired):
            pass
        if proc.poll() is None:
            proc.kill()
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _collect_worker(cmd, limit, startup_limit):
    """Drain both pipes concurrently with separate startup and work limits."""
    events = queue.Queue()
    captured = {'stdout': [], 'stderr': []}
    options = (dict(creationflags=subprocess.CREATE_NO_WINDOW) if os.name == 'nt'
               else dict(start_new_session=True))
    spawned = time.perf_counter()
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding='utf-8',
                                errors='replace', bufsize=1, env=os.environ.copy(), **options)
    except OSError as exc:
        return dict(status='STARTUP_ERROR', phase='startup', elapsed_seconds=None,
                    message=f'{type(exc).__name__}: {exc}')

    def drain(name, stream):
        try:
            for line in stream:
                captured[name].append(line)
                events.put((name, line, time.perf_counter()))
        finally:
            events.put((name, None, time.perf_counter()))

    readers = [threading.Thread(target=drain, args=(name, getattr(proc, name)), daemon=True)
               for name in ('stdout', 'stderr')]
    for reader in readers:
        reader.start()
    started = None
    deadline = spawned + startup_limit
    eof = set()
    result = None
    try:
        while result is None:
            try:
                name, line, received = events.get(timeout=max(0, deadline-time.perf_counter()))
            except queue.Empty:
                result = dict(status='STARTUP_TIMEOUT' if started is None else 'TIMEOUT',
                              phase='startup' if started is None else 'work', elapsed_seconds=None,
                              message=('Worker did not become ready within the startup limit'
                                       if started is None else
                                       'Hard wall limit from model build through validation'))
                _kill_process_tree(proc)
                break
            if received > deadline:
                result = dict(status='STARTUP_TIMEOUT' if started is None else 'TIMEOUT',
                              phase='startup' if started is None else 'work', elapsed_seconds=None,
                              message='Worker response arrived after the hard wall deadline')
                _kill_process_tree(proc)
                break
            if line is None:
                eof.add(name)
                if len(eof) == 2:
                    result = dict(status='STARTUP_ERROR' if started is None else 'ERROR',
                                  phase='startup' if started is None else 'work', elapsed_seconds=None,
                                  message='Worker exited without a valid result')
                continue
            if name != 'stdout':
                continue
            if line.strip() == 'READY' and started is None:
                started = time.perf_counter()
                deadline = started + limit
                try:
                    proc.stdin.write('GO\n')
                    proc.stdin.flush()
                    proc.stdin.close()
                except (OSError, ValueError) as exc:
                    result = dict(status='STARTUP_ERROR', phase='handshake', elapsed_seconds=None,
                                  message=f'Worker failed before GO: {exc}')
            elif line.startswith('STARTUP_ERROR ') and started is None:
                try:
                    result = json.loads(line[len('STARTUP_ERROR '):])
                except json.JSONDecodeError:
                    result = dict(status='STARTUP_ERROR', phase='startup', elapsed_seconds=None,
                                  message='Malformed startup error response')
            elif line.startswith('RESULT ') and started is not None:
                try:
                    result = json.loads(line[len('RESULT '):])
                    if not isinstance(result, dict) or 'status' not in result:
                        raise ValueError('Result must be an object with a status')
                except (json.JSONDecodeError, ValueError) as exc:
                    result = dict(status='ERROR', elapsed_seconds=None,
                                  message=f'Malformed worker result: {exc}')
        finished = time.perf_counter()
    finally:
        # Interpreter shutdown is outside elapsed_seconds but cleanup is bounded.
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _kill_process_tree(proc)
            proc.wait(timeout=5)
        for reader in readers:
            reader.join(timeout=1)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            if stream and not stream.closed:
                stream.close()
    result['startup_seconds'] = (started if started is not None else finished) - spawned
    result['observed_wall_seconds'] = finished-started if started is not None else None
    result['returncode'] = proc.returncode
    result['stdout'] = ''.join(line for line in captured['stdout']
                               if line.strip() != 'READY'
                               and not line.startswith(('RESULT ', 'STARTUP_ERROR ')))
    result['stderr'] = ''.join(captured['stderr'])
    return result


def run_one(method,n,rep,limit,startup_limit=120):
    if (not math.isfinite(limit) or limit <= 0 or
            not math.isfinite(startup_limit) or startup_limit <= 0):
        raise ValueError('Time limits must be finite positive numbers')
    record = dict(method=method,n=n,repeat=rep,limit_seconds=limit,
                  startup_limit_seconds=startup_limit,
                  timestamp=datetime.now(timezone.utc).isoformat())
    pair_count = 2*n+n*(n-1)*(5*n-1)//3
    if method=='pairwise' and pair_count>5_000_000:
        return record | dict(status='SKIPPED_RESOURCE', message='Predeclared cap 5,000,000 pairwise clauses',
                             nclauses=pair_count,nvars=n*n,elapsed_seconds=None)
    cmd=[sys.executable,'-u',str(Path(__file__).resolve()),'--worker','--method',method,
         '--n',str(n),'--limit',str(limit)]
    return record | _collect_worker(cmd,limit,startup_limit)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--worker',action='store_true'); p.add_argument('--method'); p.add_argument('--n',type=int)
    p.add_argument('--limit',type=float,default=30)
    p.add_argument('--startup-limit',type=float,default=120)
    p.add_argument('--suite',choices=['main','large','smoke'],default='main')
    p.add_argument('--output',default=None)
    p.add_argument('--methods',nargs='+',choices=ENCODINGS+BACKENDS)
    args=p.parse_args()
    if args.worker: worker(args); return
    output=Path(args.output) if args.output else ROOT/'results'/args.suite
    output.mkdir(parents=True,exist_ok=True)
    (output/'environment.json').write_text(json.dumps(environment(),indent=2),encoding='utf-8')
    if args.suite=='main':
        tasks=[(m,n,r) for n in [8,16,32,64,128] for m in ENCODINGS+BACKENDS for r in range(1,4)]
    elif args.suite=='large':
        tasks=[(m,n,1) for n in [256,512,1000] for m in ENCODINGS+BACKENDS]
    else: tasks=[(m,n,1) for n in [2,4,8] for m in ENCODINGS+BACKENDS]
    random.Random(24021650).shuffle(tasks)
    if args.methods:
        tasks=[task for task in tasks if task[0] in args.methods]
    (output/'protocol.json').write_text(json.dumps(dict(
        suite=args.suite,limit_seconds=args.limit,startup_limit_seconds=args.startup_limit,
        methods=args.methods or ENCODINGS+BACKENDS,shuffle_seed=24021650,
        pairwise_clause_cap=5_000_000,tasks=len(tasks),concurrency=1,
        timing='elapsed_seconds measures build, solver setup, solve, decode and validation; excludes imports'
    ),indent=2),encoding='utf-8')
    raw=output/'raw.jsonl'
    done=set()
    if raw.exists():
        done={(r['method'],r['n'],r['repeat']) for r in map(json.loads,raw.read_text().splitlines())}
    for m,n,r in tasks:
        if (m,n,r) in done: continue
        result=run_one(m,n,r,args.limit,args.startup_limit)
        with raw.open('a',encoding='utf-8') as f: f.write(json.dumps(result,ensure_ascii=False)+'\n')
        print(f'{m:12} n={n:4} repeat={r} {result["status"]:16} {result.get("elapsed_seconds")}',flush=True)
    records=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines()]
    fields=['method','n','repeat','status','elapsed_seconds','build_seconds','solver_setup_seconds','solve_seconds','total_seconds','nvars','nclauses','verified','limit_seconds','startup_seconds','observed_wall_seconds']
    with (output/'results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(records)

if __name__=='__main__': main()
