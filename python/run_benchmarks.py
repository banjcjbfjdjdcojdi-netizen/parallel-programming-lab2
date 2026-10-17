"""
Прогон бенчмарков для matrix_seq и matrix_omp.
Использование:
    python run_benchmarks.py
Результат: results/bench.csv
"""
import os
import re
import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

# Пути к бинарникам — предполагаем, что сборка в build/
BIN_SEQ = ROOT / "build" / "matrix_seq.exe"
BIN_OMP = ROOT / "build" / "matrix_omp.exe"

SIZES = [200, 400, 800, 1200, 1600, 2000]
THREADS = [1, 2, 4, 8, 12]

RE_LINE = re.compile(
    r"size=(\d+)\s+time=([\d.eE+-]+)\s+ops=(\d+)\s+gflops=([\d.eE+-]+)\s+threads=(\d+)"
)


def run(cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        print("STDOUT:", p.stdout)
        print("STDERR:", p.stderr)
        raise RuntimeError(f"Command failed: {' '.join(str(c) for c in cmd)}")
    return p.stdout.strip()


def parse_line(line):
    m = RE_LINE.search(line)
    if not m:
        raise ValueError(f"cannot parse: {line}")
    return {
        "size": int(m.group(1)),
        "time": float(m.group(2)),
        "ops": int(m.group(3)),
        "gflops": float(m.group(4)),
        "threads": int(m.group(5)),
    }


def main():
    if not BIN_SEQ.exists() or not BIN_OMP.exists():
        print(f"ERROR: binaries not found.")
        print(f"  expected: {BIN_SEQ}")
        print(f"  expected: {BIN_OMP}")
        print(f"Build first:  cmake --build build")
        return 1

    rows = []
    for n in SIZES:
        a = DATA / f"a_{n}.txt"
        b = DATA / f"b_{n}.txt"
        if not (a.exists() and b.exists()):
            print(f"[skip] N={n}: input files not found")
            continue

        # --- seq ---
        out = RESULTS / f"c_seq_{n}.txt"
        print(f"[seq] N={n} ...", end=" ", flush=True)
        line = run([str(BIN_SEQ), "--a", str(a), "--b", str(b), "--out", str(out)])
        print(line)
        d = parse_line(line)
        d.update({"version": "seq", "threads": 1})
        rows.append(d)

        # --- omp with different thread counts ---
        for t in THREADS:
            out = RESULTS / f"c_omp_{n}_t{t}.txt"
            env = os.environ.copy()
            env["OMP_NUM_THREADS"] = str(t)
            print(f"[omp] N={n} threads={t} ...", end=" ", flush=True)
            line = run([str(BIN_OMP), "--a", str(a), "--b", str(b), "--out", str(out)], env=env)
            print(line)
            d = parse_line(line)
            d.update({"version": "omp"})
            rows.append(d)

    csv_path = RESULTS / "bench.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["version", "size", "threads", "time", "ops", "gflops"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    print(f"\n✅ Saved: {csv_path}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()