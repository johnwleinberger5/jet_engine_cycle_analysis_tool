#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/solver"

echo "Installing C++ dependencies (Conan)..."
conan install . --output-folder=build --build=missing \
    -s build_type=Release \
    -s compiler.cppstd=17

echo "Configuring build (CMake)..."
cmake -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake

echo "Building solver..."
cmake --build build --config Release

echo "Done. Binary is at solver/build/Release/solver.exe (Windows) or solver/build/solver (Linux/Mac)"
