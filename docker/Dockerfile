# ── Stage 1: Build C++ solver ─────────────────────────────────────────────
FROM python:3.13-slim AS solver-build

RUN apt-get update && apt-get install -y \
    gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

# Pin CMake and Conan to match local dev environment
RUN pip install --no-cache-dir "cmake==3.24.*" "conan==2.29.0"

WORKDIR /build/solver
COPY solver/ .

RUN conan profile detect --force
RUN conan install . --output-folder=build --build=missing \
    -s build_type=Release \
    -s compiler=gcc \
    -s compiler.cppstd=17 \
    -s compiler.libcxx=libstdc++11
RUN cmake -B build \
    -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake \
    -DCMAKE_BUILD_TYPE=Release
RUN cmake --build build


# ── Stage 2: Runtime ──────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

# Install Python dependencies first — isolated from source so pip cache
# is only busted when pyproject.toml changes, not on every source edit
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source after install — changes here don't bust the pip layer
COPY pipeline/ pipeline/
COPY scripts/ scripts/

# Copy compiled solver binary from build stage
COPY --from=solver-build /build/solver/build/solver solver/build/solver

# Write plots to /app/outputs — mount a host volume here to retrieve them:
#   docker run --rm -v "$(pwd)/outputs:/app/outputs" engine-analysis
RUN mkdir -p outputs

CMD ["python", "scripts/run_trade_study.py"]
