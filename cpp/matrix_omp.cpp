// matrix_omp.cpp - параллельное умножение матриц через OpenMP
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <cstdlib>
#include <omp.h>

using Matrix = std::vector<std::vector<int>>;

Matrix readMatrix(const std::string& path, int& n) {
    std::ifstream fin(path);
    if (!fin) {
        std::cerr << "ERROR: cannot open " << path << "\n";
        std::exit(1);
    }
    fin >> n;
    Matrix m(n, std::vector<int>(n));
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            fin >> m[i][j];
    return m;
}

void writeMatrix(const std::string& path, const Matrix& m) {
    std::ofstream fout(path);
    if (!fout) {
        std::cerr << "ERROR: cannot write " << path << "\n";
        std::exit(1);
    }
    int n = (int)m.size();
    fout << n << "\n";
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            fout << m[i][j];
            if (j + 1 < n) fout << ' ';
        }
        fout << '\n';
    }
}

// Параллельное умножение C = A * B
Matrix multiplyOMP(const Matrix& A, const Matrix& B) {
    int n = (int)A.size();
    Matrix C(n, std::vector<int>(n, 0));

#pragma omp parallel for schedule(static)
    for (int i = 0; i < n; ++i) {
        for (int k = 0; k < n; ++k) {
            int aik = A[i][k];
            int* Crow = C[i].data();
            const int* Brow = B[k].data();
            for (int j = 0; j < n; ++j) {
                Crow[j] += aik * Brow[j];
            }
        }
    }
    return C;
}

int main(int argc, char** argv) {
    std::string pathA, pathB, pathOut;
    for (int i = 1; i + 1 < argc; i += 2) {
        std::string key = argv[i];
        std::string val = argv[i + 1];
        if (key == "--a") pathA = val;
        else if (key == "--b") pathB = val;
        else if (key == "--out") pathOut = val;
    }
    if (pathA.empty() || pathB.empty() || pathOut.empty()) {
        std::cerr << "Usage: matrix_omp --a <A.txt> --b <B.txt> --out <C.txt>\n";
        return 1;
    }

    int nA = 0, nB = 0;
    Matrix A = readMatrix(pathA, nA);
    Matrix B = readMatrix(pathB, nB);
    if (nA != nB) {
        std::cerr << "ERROR: matrices must be square and same size\n";
        return 1;
    }
    int n = nA;

    int usedThreads = 0;
    auto t1 = std::chrono::high_resolution_clock::now();
    Matrix C = multiplyOMP(A, B);
    auto t2 = std::chrono::high_resolution_clock::now();
    double sec = std::chrono::duration<double>(t2 - t1).count();

#pragma omp parallel
    {
#pragma omp master
        usedThreads = omp_get_num_threads();
    }

    writeMatrix(pathOut, C);

    double ops = 2.0 * n * n * n;
    double gflops = ops / sec / 1e9;
    std::cout << "size=" << n
        << " time=" << sec
        << " ops=" << (long long)ops
        << " gflops=" << gflops
        << " threads=" << usedThreads << "\n";
    return 0;
}