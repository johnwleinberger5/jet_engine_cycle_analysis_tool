# Jet Engine Cycle Analysis Tool

![CI](https://github.com/johnwleinberger5/jet_engine_cycle_analysis_tool/actions/workflows/ci.yml/badge.svg)

A physics-based 1D Brayton cycle simulator demonstrating end-to-end production software
practices: a compiled C++ solver orchestrated by Python, built with CMake + Conan,
containerized with Docker, and validated by a full CI/CD pipeline on every push.
See the [auto-generated documentation](https://johnwleinberger5.github.io/jet_engine_cycle_analysis_tool/)
for physics, equations, assumptions, and a full module reference.

> The emphasis is on production software engineering practices — the physics are representative but intentionally simplified.

---

<p align="center"><img src="assets/jet_engine_cross_section.svg" width="680" alt="Jet engine cross-section diagram"/></p>

---

## Quick start

### Prerequisites

| Tool | Purpose |
|---|---|
| Python 3.13 | Pipeline orchestration |
| Visual Studio 2022 (Desktop C++ workload) | C++17 compiler + CMake |
| Conan 2.x | C++ dependency manager |
| Docker Desktop | Containerized execution (optional) |

> CMake must be on PATH outside the Developer Command Prompt — see the Conan profile
> setup step below. Conan must be installed globally (not inside the venv), along with
> its dependencies: `pip install conan colorama` (run outside the venv).

---

### 1 — Set up the Python environment

Run once from the repo root in Git Bash:

```bash
bash scripts/setup_env.sh
source .venv/Scripts/activate   # Git Bash
# or
.venv\Scripts\Activate.ps1      # PowerShell
```

| Action | Git Bash | PowerShell |
|---|---|---|
| Activate | `source .venv/Scripts/activate` | `.venv\Scripts\Activate.ps1` |
| Deactivate | `deactivate` | `deactivate` |

---

### 2 — Build the C++ solver

Run from the repo root (venv does not need to be active):

```bash
bash build_solver.sh
```

Flags:

| Flag | Effect |
|---|---|
| *(none)* | Release build (default) |
| `--release` | Explicit Release build |
| `--debug` | Debug build |
| `--clean` | Delete `solver/build/` before building |

> First-time Conan setup (Developer Command Prompt, run once):
> ```cmd
> conan profile detect
> conan profile show
> ```

---

### 3 — Run tests

Runs C++ tests (CTest) and Python tests (pytest). Requires the solver to be built and the venv active:

```bash
bash run_tests.sh
```

---

### 4 — Run the trade study

**Option A — Local** (venv active, solver built):

```bash
python scripts/run_trade_study.py
```

**Option B — Docker** (no local build required):

```bash
bash run_docker.sh
```

Flags for `run_docker.sh`:

| Flag | Effect |
|---|---|
| *(none)* | Use cached Docker image if available |
| `--no-cache` | Force clean image rebuild |

Plots are written to `outputs/` in both cases.

---

### 5 — Build documentation

Requires the trade study to have been run first (plots must exist in `outputs/`):

```bash
bash scripts/build_docs.sh
```

Output is written to `site/`. Open locally:

```bash
start msedge "$(pwd -W)/site/pipeline.html"
```

> The root `site/index.html` redirect does not work on local `file://` URLs —
> open `site/pipeline.html` directly.
