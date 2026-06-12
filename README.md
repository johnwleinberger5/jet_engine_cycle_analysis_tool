# Jet Engine Cycle Analysis Tool

![CI](https://github.com/johnwleinberger5/jet_engine_cycle_analysis_tool/actions/workflows/ci.yml/badge.svg)

A physics-based 1D Brayton cycle simulator demonstrating end-to-end production software practices: a compiled C++ solver orchestrated by Python, built with CMake + Conan, containerized with Docker, and validated by a full CI/CD pipeline on every push.

---

<p align="center"><img src="assets/jet_engine_cross_section.svg" width="680" alt="Jet engine cross-section diagram"/></p>

---

## What this is (and isn't)

This is a **toy problem by design.** The physics are intentionally simplified — calorically perfect gas, fixed TIT, zero bypass ratio, no stage-by-stage turbomachinery — so the focus stays on software engineering quality rather than solver fidelity. The README documents every simplification honestly.

A higher-fidelity version would add variable TIT sweeps, turbofan bypass ratio, real gas properties (NASA-7 polynomials), and oblique shock inlet modeling. A full production solver would couple 1D meanline turbomachinery with CFD for individual components and run a complete mission analysis across climb, cruise, and descent.

---

## Trade study outputs

The tool sweeps OPR (10–40) against Mach (0.5–1.7) at 60,000 ft, producing contour plots of specific thrust (N per kg/s) and SFC (kg/s/N) with a representative Symphony-like operating point marked at OPR ≈ 25, Mach 1.7.

*Plots are generated at runtime and uploaded as CI artifacts on every workflow run.*

---

## Stack

| Layer | Technology |
|---|---|
| Physics solver | C++17, CMake, Conan |
| Orchestration | Python 3.11, subprocess, numpy |
| Visualization | matplotlib |
| Dependency management | Conan (C++), pyproject.toml (Python) |
| Containerization | Docker (multi-stage build) |
| CI/CD | GitHub Actions |
| Documentation | pdoc (auto-generated from docstrings) |

---

## Architecture

Python calls the C++ solver as a subprocess, exchanging JSON on stdin/stdout. This clean interface means the solver can be swapped for a pybind11 shared library by changing a single file (`pipeline/solver_interface.py`) without touching the rest of the stack.

```
scripts/run_trade_study.py
    └── pipeline/trade_study.py          # OPR × Mach grid sweep
        └── pipeline/solver_interface.py # subprocess + JSON protocol
            └── solver/                  # C++ binary (CMake + Conan)
    └── pipeline/plotting.py             # matplotlib contour plots
```

**Solver I/O contract**

Input JSON: `mach`, `opr`, `tit_k`, `altitude_ft`

Output JSON: `specific_thrust_n_per_kgs`, `sfc_kg_per_s_per_n`, `t0_stations_k[6]`, `p0_stations_pa[6]`

Stations follow the diagram above: freestream → inlet exit → compressor exit → combustor exit → turbine exit → nozzle exit.

---

## CI/CD pipeline

Every push triggers a three-stage GitHub Actions workflow:

1. **Build** — Conan installs C++ dependencies, CMake builds and links the solver binary, C++ unit tests run via CTest.
2. **Test** — pytest runs the Python test suite (solver interface, atmosphere model, trade study numerics, regression tests against known outputs).
3. **Trade study** — the full OPR × Mach sweep executes and both contour plots are uploaded as workflow artifacts.

---

## Run with Docker (recommended)

```powershell
docker build -f docker/Dockerfile -t engine-analysis .
docker run --rm -v "${PWD}/outputs:/app/outputs" engine-analysis
```

Plots are written to `outputs/`.

---

## Run natively

**Prerequisites:** Python 3.13, CMake 3.24+, Conan 2.29.0, a C++17 compiler. See [Development environment setup](#development-environment-setup-windows) below.

**First time — create and activate the Python virtual environment:**

```bash
# Git Bash (repo root)
bash scripts/setup_env.sh
source ".venv\Scripts\activate"
```

**Every subsequent session — activate before doing anything else:**

```bash
source ".venv\Scripts\activate"   # Git Bash
# or
.venv\Scripts\activate          # PowerShell
```

**Build the C++ solver** (Developer Command Prompt, from repo root):

```cmd
bash build_solver.sh
```

Or manually:

```cmd
cd solver
conan install . --output-folder=build --build=missing -s build_type=Release -s compiler.cppstd=17
cmake -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
cd ..
```

> CMake is only on PATH inside the Developer Command Prompt. Run build commands there, not in Git Bash or PowerShell.

**Run the trade study** (Git Bash or PowerShell, venv active):

```bash
python scripts/run_trade_study.py
```

**Run tests:**

```bash
pytest tests/
```

**Deactivate the virtual environment when done:**

```bash
deactivate
```

> Conan is installed globally and must not be installed inside the venv. Always activate the venv before running Python pipeline commands locally.

---

## Development environment setup (Windows)

Docker is the recommended way to run the tool reproducibly. The native setup below is for active development.

### Required tools

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13 | Pipeline orchestration |
| Visual Studio 2022 Community | MSVC 19.34 | C++17 compiler + CMake |
| Conan | 2.x | C++ dependency manager |
| Docker Desktop | 4.41+ | Containerized execution |
| WSL2 | 2.7+ | Required by Docker Desktop |

### Python 3.13

Download from [python.org](https://python.org). During install, check **"Add Python to PATH"**.

```powershell
python --version  # verify
```

### Visual Studio 2022 Community (C++ compiler + CMake)

Download from [visualstudio.microsoft.com](https://visualstudio.microsoft.com). Select the **"Desktop development with C++"** workload — this installs MSVC and CMake together.

Verify by opening **x64 Native Tools Command Prompt for VS 2022**:

```cmd
cl          # C++ compiler
cmake --version
```

> `cl` is only on PATH inside the Developer Command Prompt. CMake and Conan locate it automatically — you never need to invoke `cl` directly for this project.

**Add CMake to your system PATH** so it can be found from Git Bash and PowerShell as well. First find the CMake binary installed by Visual Studio — run this in the Developer Command Prompt:

```cmd
where cmake
```

It will print something like:
```
C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe
```

Copy everything up to (and including) `\bin` — that is the directory to add. Then:

*Start menu → "Edit the system environment variables" → Environment Variables → System variables → Path → Edit → New → paste the path → OK*

Open a new terminal and verify:

```bash
cmake --version  # should work in Git Bash and PowerShell now
```

### Conan 2.x

Install from PowerShell (not Git Bash, not the Developer Command Prompt):

```powershell
pip install conan
```

Add the Python Scripts folder to your system PATH if it isn't already:
`C:\Users\<username>\AppData\Local\Programs\Python\Python313\Scripts\`

*Start menu → "Edit the system environment variables" → Environment Variables → System Variables → Path → Edit → New*

Initialize the default Conan profile from the **Developer Command Prompt** so it detects MSVC:

```cmd
conan profile detect
conan profile show  # verify MSVC is detected
```

### WSL2 + Docker Desktop

Install WSL2 first (PowerShell as Administrator), then restart:

```powershell
wsl --install
```

Download **Docker Desktop for Windows (AMD64)** from [docker.com](https://docker.com). After install and restart, open Docker Desktop and wait for "Engine running".

```powershell
docker --version
docker run hello-world  # verify
```

### Python virtual environment

Run the setup script once from the repo root in Git Bash — it creates the venv and installs all dependencies from `pyproject.toml`:

```bash
bash scripts/setup_env.sh
```

| Action | Git Bash | PowerShell |
|---|---|---|
| Activate | `source ".venv\Scripts\activate"` | `.venv\Scripts\activate` |
| Deactivate | `deactivate` | `deactivate` |
| Add a dependency | edit `pyproject.toml`, then `pip install -e .` | same |
| Check active venv | `which python` | `where python` |

The venv prompt prefix `(.venv)` confirms it is active. Conan is installed globally and must not go inside the venv — it needs to detect MSVC from outside.

> Docker is the source of truth for reproducible execution. The local venv setup is for development convenience only.
