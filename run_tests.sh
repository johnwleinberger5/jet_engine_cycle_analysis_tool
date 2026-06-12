#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

run_suite() {
    local name="$1"
    shift
    echo ""
    echo "======== $name ========"
    if "$@"; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
    fi
}

# C++ tests (CTest) — skipped gracefully if the build directory doesn't exist
if [ -d "solver/build" ]; then
    run_suite "C++ (CTest)" ctest --test-dir solver/build --output-on-failure -C Release
else
    echo ""
    echo "======== C++ (CTest) ========"
    echo "SKIP: solver/build not found - run ./build_solver.sh first"
fi

# Python tests (pytest)
run_suite "Python (pytest)" pytest tests/

echo ""
echo "========================================"
echo "Results: $PASS suite(s) passed, $FAIL suite(s) failed"
echo "========================================"

[ "$FAIL" -eq 0 ]
