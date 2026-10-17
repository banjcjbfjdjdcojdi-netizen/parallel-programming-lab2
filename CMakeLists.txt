cmake_minimum_required(VERSION 3.15)
project(lab1_parallel CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# По умолчанию - Release с оптимизацией
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Оптимизация для GCC/MinGW
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    set(CMAKE_CXX_FLAGS_RELEASE "-O2")
endif()

# --- Последовательная версия ---
add_executable(matrix_seq cpp/matrix_seq.cpp)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(matrix_seq PRIVATE -Wall -Wextra)
endif()

# --- OpenMP версия ---
find_package(OpenMP REQUIRED)
add_executable(matrix_omp cpp/matrix_omp.cpp)
target_link_libraries(matrix_omp PRIVATE OpenMP::OpenMP_CXX)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(matrix_omp PRIVATE -Wall -Wextra)
endif()

# Создать папки данных
file(MAKE_DIRECTORY ${CMAKE_SOURCE_DIR}/data)
file(MAKE_DIRECTORY ${CMAKE_SOURCE_DIR}/results)

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "OpenMP found: ${OpenMP_CXX_FOUND}")