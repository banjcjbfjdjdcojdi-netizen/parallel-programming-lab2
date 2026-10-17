"""
Генератор входных матриц.
Использование:
    python gen_matrices.py 100 300 500
Создаёт data/a_N.txt и data/b_N.txt с целыми 0..9.
"""
import sys
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def gen_matrix(n, path, rng):
    with open(path, "w") as f:
        f.write(f"{n}\n")
        for _ in range(n):
            row = " ".join(str(rng.randint(0, 9)) for _ in range(n))
            f.write(row + "\n")


def main(sizes):
    rng = random.Random(42)  # фиксированный seed для воспроизводимости
    for n in sizes:
        a_path = DATA_DIR / f"a_{n}.txt"
        b_path = DATA_DIR / f"b_{n}.txt"
        if a_path.exists() and b_path.exists():
            print(f"[skip] N={n} already exists")
            continue
        print(f"[gen]  N={n} ...", end=" ", flush=True)
        gen_matrix(n, a_path, rng)
        gen_matrix(n, b_path, rng)
        print("done")
    print(f"\nFiles in {DATA_DIR}:")
    for p in sorted(DATA_DIR.glob("*.txt")):
        print(f"  {p.name}  ({p.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    sizes = [int(x) for x in sys.argv[1:]] or [100, 300, 500]
    main(sizes)