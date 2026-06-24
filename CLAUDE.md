# Engine Cycle Analysis Tool — Project Context

## Acronyms
- OPR: Overall Pressure Ratio
- TIT: Turbine Inlet Temperature
- SFC: Specific Fuel Consumption
- LHV: Lower Heating Value
- SAF: Sustainable Aviation Fuel
- CI/CD: Continuous Integration / Continuous Deployment
- stdatm: Standard Atmosphere
- P0: Total (stagnation) pressure
- T0: Total (stagnation) temperature
- gamma: Ratio of specific heats (1.4 for calorically perfect air)
- cp: Specific heat at constant pressure
- eta_c: Compressor isentropic efficiency
- eta_t: Turbine isentropic efficiency
- eta_b: Combustor efficiency
- mdot_a: Mass flow rate of air
- mdot_f: Mass flow rate of fuel
- V_exit: Nozzle exit velocity
- V_inlet: Inlet freestream velocity

## Project Purpose

This project is a jet engine cycle analysis tool built to demonstrate
end-to-end software engineering practices applied to a physics-based
aerospace simulation. The emphasis is on production software quality:
clean architecture, testing, containerization, CI/CD, and reproducible
environments, with a propulsion simulation core that is intentionally
simple but physically representative and extensible.

The simulation is a toy problem by design. The physics, assumptions, and
higher-fidelity roadmap are documented in pipeline/physics.py (rendered
in the auto-generated docs).

## What This Project Demonstrates

- Python orchestration layer wrapping a compiled C++ solver via subprocess
- Clean API boundary between Python and C++ (JSON I/O protocol)
- CMake + Conan build system for the C++ module
- pytest suite covering solver numerics and regression tests on outputs
- Dockerfile for fully reproducible containerized execution
- GitHub Actions CI: build C++ → run tests → trade study → Docker → deploy docs
- Auto-generated Python documentation (pdoc) deployed to GitHub Pages
- Structured, readable codebase with a senior engineering audience in mind

## Physics — What We're Modeling

A 1D Brayton cycle engine model with the following station-by-station flow.
Stations are indexed 0-5 throughout the code and documentation.

Station 0 — Freestream (isentropic ram):
Standard atmosphere at fixed altitude (60,000 ft) sets ambient P, T, density.
```
T0[0] = T_amb × (1 + (gamma-1)/2 × M²)
P0[0] = P_amb × (T0[0] / T_amb)^(gamma/(gamma-1))
V_inlet = M × sqrt(gamma × R × T_amb)
```

Station 1 — Inlet exit (normal shock):
T0 is conserved across an adiabatic shock. Total pressure recovery uses
the Rayleigh Pitot formula (exact closed form). Recovery = 1.0 for M ≤ 1.
```
T0[1] = T0[0]
P0[1] = P0[0] × recovery(M, gamma)
```

Station 2 — Compressor exit (isentropic efficiency eta_c):
```
T0[2] = T0[1] × (1 + (OPR^((gamma-1)/gamma) - 1) / eta_c)
P0[2] = P0[1] × OPR
```

Station 3 — Combustor exit / turbine inlet:
Fixed TIT. Fuel-air ratio from energy balance. Combustor pressure drop neglected.
```
T0[3] = TIT  (fixed at 1600 K)
P0[3] = P0[2]
f = cp × (TIT - T0[2]) / (eta_b × LHV)    where f = mdot_f / mdot_a
```

Station 4 — Turbine exit (isentropic efficiency eta_t):
Power balance (neglecting fuel mass fraction ~1.6% error):
```
T0[4] = TIT - (T0[2] - T0[1])              (actual exit temperature, independent of eta_t)
T0_4s = TIT - (T0[2] - T0[1]) / eta_t     (isentropic equivalent for pressure calc)
P0[4] = P0[3] × (T0_4s / TIT)^(gamma/(gamma-1))
```

Station 5 — Nozzle exit (isentropic expansion to ambient):
```
T_exit = T0[4] × (P_amb / P0[4])^((gamma-1)/gamma)
V_exit = sqrt(2 × cp × (T0[4] - T_exit))
T0[5] = T0[4]   (adiabatic nozzle)
P0[5] = P0[4]   (isentropic nozzle)
```

Performance Outputs:
```
Specific thrust = V_exit - V_inlet   [N/(kg/s)]
SFC = f / (V_exit - V_inlet)         [kg/(N*s)]
```

## Fixed Parameters

- Altitude: 60,000 ft (standard atmosphere sets ambient P, T, density)
- TIT: 1600 K (fixed for base trade study)
- Bypass ratio: 0 (pure turbojet)
- gamma: 1.4 (calorically perfect gas)
- cp: 1005 J/(kg*K)
- eta_c (compressor isentropic efficiency): 0.88
- eta_t (turbine isentropic efficiency): 0.90
- eta_b (combustor efficiency): 0.99
- LHV (fuel lower heating value): 43 MJ/kg (Jet-A)

## Trade Study

Sweep: OPR (10-40, 30 steps) × Mach (0.5-1.7, 26 steps)
Fixed: TIT = 1600 K, altitude = 60,000 ft
Outputs:
- Specific thrust grid plot (N/(kg/s))
- SFC grid plot (mg/(s*N)) — scaled from kg/(N*s) for readability
- Both plots with a representative Symphony-like operating point marked
  (OPR ≈ 25, Mach 1.7 — illustrative only, not derived from proprietary data)

## C++ Solver Interface (subprocess)

The C++ solver is a standalone executable built with CMake and Conan.
Python calls it via subprocess, passing conditions as a JSON string on
stdin and receiving results as JSON on stdout.

Input JSON schema:
    mach: float
    opr: float
    tit_k: float
    altitude_ft: float

Output JSON schema:
    specific_thrust_n_per_kgs: float
    sfc_kg_per_s_per_n: float
    t0_stations_k: list of 6 floats
    p0_stations_pa: list of 6 floats

Station order for both lists:
[freestream, inlet exit, compressor exit, combustor exit, turbine exit,
nozzle exit]

## Repo Structure

jet_engine_cycle_analysis_tool/
    CLAUDE.md
    README.md
    pyproject.toml
    build_solver.sh
    run_tests.sh
    run_docker.sh
    assets/
        jet_engine_cross_section.svg
    solver/
        CMakeLists.txt
        CMakeUserPresets.json
        conanfile.txt
        main.cpp
        config/
            config.json
        src/
            engine_cycle.cpp
            engine_cycle.h
            atmosphere.cpp
            atmosphere.h
            thermo_utils.h
            constants.h
            error_utils.h
        tests/
            test_solver.cpp
    pipeline/
        __init__.py
        constants.py
        atmosphere.py
        solver_interface.py
        trade_study.py
        plotting.py
        physics.py
        acronyms.py
        changelog.py
    tests/
        conftest.py
        test_solver_interface.py
        test_atmosphere.py
        test_trade_study.py
        test_regression.py
    scripts/
        run_trade_study.py
        setup_env.sh
        build_docs.sh
    outputs/
    site/
    docker/
        Dockerfile
    .github/
        workflows/
            ci.yml

## README Structure

The README.md is a quick-start guide for a first-time user cloning the repo:
1. Title + CI badge
2. Two-sentence project overview + link to auto-generated docs
3. Blockquote emphasising the software engineering focus
4. SVG station diagram
5. How to run (5 steps): set up Python environment, build solver,
   run tests, run trade study (local or Docker), build docs

Full physics, equations, assumptions, and higher-fidelity roadmap are
documented in the auto-generated docs (pipeline/physics.py).

## Development Notes for Claude Code

Build order:
1. C++ solver first — validate against known analytical limits (OPR=1
   should give near-zero specific thrust above inlet ram contribution;
   TIT equal to ambient temperature should give near-zero SFC)
2. Python subprocess wrapper second — test with mock solver output before
   wiring to the real binary
3. Trade study sweep third — vectorized OPR and Mach grid, results to
   numpy array
4. Plotting fourth — matplotlib pcolormesh plots with Symphony operating
   point marker
5. Docker and CI last — wrap everything once working locally

Other notes:
- Keep each module independently testable
- solver_interface.py should work with a mock binary for CI environments
  where the C++ build might not be available
- All physical constants in a single constants.py file — no magic numbers
  anywhere else
- The Python/C++ interface is designed so that swapping the subprocess
  solver for a nanobind shared library later requires changes only to
  solver_interface.py
