#!/usr/bin/env bash
set -euo pipefail

CLEAN=""
BUILD_TYPE="Release"

for arg in "$@"; do
    case "$arg" in
        --clean)   CLEAN=1 ;;
        --release) BUILD_TYPE="Release" ;;
        --debug)   BUILD_TYPE="Debug" ;;
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
    -s build_type="$BUILD_TYPE" \
    -s compiler.cppstd=17

echo "Configuring build (CMake)..."
cmake -B build \
    -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake \
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE"

echo "Building solver ($BUILD_TYPE)..."
cmake --build build --config "$BUILD_TYPE"

echo "Done. Binary is at solver/build/$BUILD_TYPE/solver.exe (Windows) or solver/build/solver (Linux/Mac)"
