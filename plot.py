"""
Построение графиков по результатам бенчмарка.
Использование:
    python scripts/plot_results.py
Читает results/bench.csv, сохраняет графики в results/plots/.
"""
import csv
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")  # без GUI
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "results" / "bench.csv"
OUT = ROOT / "results" / "plots"
OUT.mkdir(exist_ok=True)


def load_data():
    rows = []
    with open(CSV) as f:
        for r in csv.DictReader(f):
            rows.append({
                "version": r["version"],
                "size": int(r["size"]),
                "threads": int(r["threads"]),
                "time": float(r["time"]),
                "ops": int(r["ops"]),
                "gflops": float(r["gflops"]),
            })
    return rows


def plot_time_vs_size(rows):
    """Время vs размер для разных конфигураций."""
    fig, ax = plt.subplots(figsize=(9, 6))

    # seq
    seq = sorted([r for r in rows if r["version"] == "seq"], key=lambda x: x["size"])
    ax.plot([r["size"] for r in seq], [r["time"] for r in seq],
            "o-", label="seq", color="black", linewidth=2, markersize=8)

    # omp для потоков 1, 2, 4, 8, 12
    for t in [1, 2, 4, 8, 12]:
        omp = sorted([r for r in rows if r["version"] == "omp" and r["threads"] == t],
                     key=lambda x: x["size"])
        if omp:
            ax.plot([r["size"] for r in omp], [r["time"] for r in omp],
                    "s--", label=f"omp t={t}", markersize=6)

    ax.set_xlabel("Размер матрицы N")
    ax.set_ylabel("Время умножения, сек")
    ax.set_title("Время умножения матриц N×N")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "time_vs_size.png", dpi=150)
    plt.close(fig)
    print(f"  saved: {OUT / 'time_vs_size.png'}")


def plot_speedup(rows):
    """Ускорение vs число потоков."""
    fig, ax = plt.subplots(figsize=(9, 6))
    sizes = sorted({r["size"] for r in rows})

    for n in sizes:
        seq = [r for r in rows if r["version"] == "seq" and r["size"] == n]
        if not seq:
            continue
        t_seq = seq[0]["time"]
        omp = sorted([r for r in rows if r["version"] == "omp" and r["size"] == n],
                     key=lambda x: x["threads"])
        threads = [r["threads"] for r in omp]
        speedup = [t_seq / r["time"] for r in omp]
        ax.plot(threads, speedup, "o-", label=f"N={n}", markersize=8, linewidth=2)

    # Идеальная линия
    max_t = max(r["threads"] for r in rows if r["version"] == "omp")
    xs = np.linspace(1, max_t, 100)
    ax.plot(xs, xs, "k--", alpha=0.5, label="Идеальное ускорение (y=x)")

    ax.set_xlabel("Число потоков")
    ax.set_ylabel("Ускорение (Speedup = T_seq / T_omp)")
    ax.set_title("Ускорение OpenMP относительно последовательной версии")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "speedup_vs_threads.png", dpi=150)
    plt.close(fig)
    print(f"  saved: {OUT / 'speedup_vs_threads.png'}")


def plot_gflops(rows):
    """GFLOPS vs число потоков."""
    fig, ax = plt.subplots(figsize=(9, 6))
    sizes = sorted({r["size"] for r in rows})

    for n in sizes:
        omp = sorted([r for r in rows if r["version"] == "omp" and r["size"] == n],
                     key=lambda x: x["threads"])
        threads = [r["threads"] for r in omp]
        gflops = [r["gflops"] for r in omp]
        ax.plot(threads, gflops, "o-", label=f"omp N={n}", markersize=8, linewidth=2)

    ax.set_xlabel("Число потоков")
    ax.set_ylabel("Производительность, GFLOPS")
    ax.set_title("Производительность OpenMP-версии")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "gflops_vs_threads.png", dpi=150)
    plt.close(fig)
    print(f"  saved: {OUT / 'gflops_vs_threads.png'}")


def plot_efficiency(rows):
    """Эффективность (speedup / threads) vs число потоков."""
    fig, ax = plt.subplots(figsize=(9, 6))
    sizes = sorted({r["size"] for r in rows})

    for n in sizes:
        seq = [r for r in rows if r["version"] == "seq" and r["size"] == n]
        if not seq:
            continue
        t_seq = seq[0]["time"]
        omp = sorted([r for r in rows if r["version"] == "omp" and r["size"] == n],
                     key=lambda x: x["threads"])
        threads = [r["threads"] for r in omp]
        eff = [100.0 * (t_seq / r["time"]) / r["threads"] for r in omp]
        ax.plot(threads, eff, "o-", label=f"N={n}", markersize=8, linewidth=2)

    ax.set_xlabel("Число потоков")
    ax.set_ylabel("Эффективность, % (Speedup / Threads × 100)")
    ax.set_title("Эффективность распараллеливания")
    ax.axhline(100, color="k", linestyle="--", alpha=0.5, label="Идеал (100%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim(0, 110)
    fig.tight_layout()
    fig.savefig(OUT / "efficiency_vs_threads.png", dpi=150)
    plt.close(fig)
    print(f"  saved: {OUT / 'efficiency_vs_threads.png'}")


def print_summary(rows):
    """Печатает сводную таблицу для отчёта."""
    print("\n" + "=" * 78)
    print("СВОДНАЯ ТАБЛИЦА УСКОРЕНИЯ")
    print("=" * 78)
    print(f"{'N':>5} | {'threads':>7} | {'time, s':>10} | {'speedup':>8} | {'efficiency':>10} | {'GFLOPS':>8}")
    print("-" * 78)

    sizes = sorted({r["size"] for r in rows})
    for n in sizes:
        seq = [r for r in rows if r["version"] == "seq" and r["size"] == n]
        if not seq:
            continue
        t_seq = seq[0]["time"]
        g_seq = seq[0]["gflops"]
        print(f"{n:>5} | {'seq':>7} | {t_seq:>10.5f} | {1.0:>8.2f} | {100.0:>9.1f}% | {g_seq:>8.2f}")

        omp = sorted([r for r in rows if r["version"] == "omp" and r["size"] == n],
                     key=lambda x: x["threads"])
        for r in omp:
            sp = t_seq / r["time"]
            eff = 100.0 * sp / r["threads"]
            print(f"{n:>5} | {r['threads']:>7} | {r['time']:>10.5f} | {sp:>8.2f} | {eff:>9.1f}% | {r['gflops']:>8.2f}")
        print("-" * 78)


def main():
    if not CSV.exists():
        print(f"ERROR: {CSV} not found. Run run_benchmarks.py first.")
        return
    rows = load_data()
    print(f"Loaded {len(rows)} rows from {CSV}")

    print("\nBuilding plots...")
    plot_time_vs_size(rows)
    plot_speedup(rows)
    plot_gflops(rows)
    plot_efficiency(rows)

    print_summary(rows)
    print(f"\n✅ All plots saved to {OUT}")


if __name__ == "__main__":
    main()