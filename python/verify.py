"""
Верификация результата C++ через NumPy.
Использование:
    python verify.py results/c_seq_100.txt data/a_100.txt data/b_100.txt
"""
import sys
import numpy as np
from pathlib import Path


def read_matrix(path):
    with open(path) as f:
        n = int(f.readline().strip())
        m = np.array([[int(x) for x in f.readline().split()] for _ in range(n)])
    return m


def main():
    if len(sys.argv) != 4:
        print("Usage: python verify.py <C.txt> <A.txt> <B.txt>")
        sys.exit(1)

    C_file, A_file, B_file = sys.argv[1:4]
    print(f"C++ result : {C_file}")
    print(f"A          : {A_file}")
    print(f"B          : {B_file}")

    C = read_matrix(C_file)
    A = read_matrix(A_file)
    B = read_matrix(B_file)

    print(f"Shapes: A={A.shape} B={B.shape} C={C.shape}")

    C_ref = A @ B

    if np.array_equal(C, C_ref):
        print("\n✅ MATCH: C++ result equals NumPy reference")
        sys.exit(0)
    else:
        diff = np.abs(C - C_ref)
        max_diff = int(diff.max())
        n_diff = int((diff != 0).sum())
        print(f"\n❌ MISMATCH")
        print(f"   max |diff| = {max_diff}")
        print(f"   cells with diff = {n_diff} / {C.size}")
        sys.exit(1)


if __name__ == "__main__":
    main()