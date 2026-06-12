#!/usr/bin/env bash
set -euo pipefail

CLEAN=""

for arg in "$@"; do
    case "$arg" in
        --clean) CLEAN=1 ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
done

cd "$(dirname "$0")/solver"

if [ -n "$CLEAN" ] && [ -d build ]; then
    echo "Cleaning build directory..."
    rm -rf build
fi

echo "Installing C++ dependencies (Conan)..."
conan install . --output-folder=build --build=missing \
    -s build_type=Release \
    -s compiler.cppstd=17

echo "Configuring build (CMake)..."
cmake -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake

echo "Building solver..."
cmake --build build --config Release

echo "Done. Binary is at solver/build/Release/solver.exe (Windows) or solver/build/solver (Linux/Mac)"
