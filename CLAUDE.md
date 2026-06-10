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
simple but physically honest and extensible.

The simulation is a toy problem by design. The README documents exactly
what simplifications are made, what a higher-fidelity version would look
like, and why this scope was chosen.

## What This Project Demonstrates

- Python orchestration layer wrapping a compiled C++ solver via subprocess
- Clean API boundary between Python and C++ (JSON I/O protocol)
- CMake + Conan build system for the C++ module
- pytest suite covering solver numerics and regression tests on outputs
- Dockerfile for fully reproducible containerized execution
- GitHub Actions CI: build C++ then run tests then execute trade study then upload plots as artifacts
- Auto-generated Python documentation (pdoc)
- Structured, readable codebase with a senior engineering audience in mind

## Physics — What We're Modeling

A 1D Brayton cycle engine model with the following station-by-station flow:

Station 1 — Freestream to Inlet:
Standard atmosphere at fixed altitude (60,000 ft) sets ambient P, T, and
density. Normal shock total pressure recovery as a function of Mach using
exact normal shock relations: P0_exit divided by P0_inlet equals
f(Mach, gamma). Isentropic total temperature rise from ram effect.

Station 2 — Inlet to Compressor Exit:
Isentropic compression.
T0_exit = T0_inlet times (1 + (OPR to the power of ((gamma-1)/gamma) - 1)
divided by eta_c)
P0_exit = P0_inlet times OPR

Station 3 — Compressor Exit to Turbine Inlet (Combustor):
Fixed TIT = 1600K. Fuel flow calculated from energy balance:
mdot_f = mdot_a times cp times (TIT - T0_compressor_exit) divided by
(eta_b times LHV)

Station 4 — Turbine:
Extracts work to drive compressor via power balance.
T0_exit = TIT - (T0_compressor_exit - T0_inlet_station) divided by eta_t

Station 5 — Nozzle:
Isentropic expansion to ambient pressure. Exit velocity from stagnation
enthalpy drop:
V_exit = sqrt(2 times cp times (T0_turbine_exit - T_exit))

Performance Outputs:
Specific thrust = V_exit - V_inlet (N per kg/s of airflow)
SFC = mdot_f divided by Thrust (kg per s per N)

## Fixed Parameters

- Altitude: 60,000 ft (standard atmosphere sets ambient P, T, density)
- TIT: 1600 K (fixed for base trade study)
- Bypass ratio: 0 (pure turbojet for simplicity; noted in README)
- gamma: 1.4 (calorically perfect gas)
- cp: 1005 J per kg per K
- eta_c (compressor isentropic efficiency): 0.88
- eta_t (turbine isentropic efficiency): 0.90
- eta_b (combustor efficiency): 0.99
- LHV (fuel lower heating value): 43 MJ per kg (Jet-A)

## Trade Study

Sweep: OPR (10 to 40, 30 steps) by Mach (0.5 to 1.7, 26 steps)
Fixed: TIT = 1600K, altitude = 60,000 ft
Outputs:
- Specific thrust contour plot (N per kg/s)
- SFC contour plot (kg per s per N)
- Both plots with a representative Symphony-like operating point marked
  (OPR approximately 25, Mach 1.7 — noted as illustrative in README)

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

engine-cycle-analysis/
    CLAUDE.md
    README.md
    pyproject.toml
    solver/
        CMakeLists.txt
        conanfile.txt
        src/
            main.cpp
        tests/
            test_solver.cpp
    pipeline/
        __init__.py
        solver_interface.py
        atmosphere.py
        trade_study.py
        plotting.py
    tests/
        test_solver_interface.py
        test_atmosphere.py
        test_trade_study.py
        test_regression.py
    scripts/
        run_trade_study.py
    outputs/
    docker/
        Dockerfile
    .github/
        workflows/
            ci.yml
    docs/

## README Structure

The README.md should contain the following sections in order:

1. One-line description of the project
2. CI status badge
3. Rendered trade study plots (specific thrust and SFC contours)
4. What this is and why it is a toy problem — honest disclaimer
5. What higher fidelity would look like at two levels:
   Level 1: variable TIT sweep, turbofan bypass ratio, real gas properties,
   oblique shock inlet model
   Level 2: 1D meanline turbomachinery stage-by-stage, coupled CFD for
   individual components, full mission analysis across climb/cruise/descent
6. Stack overview (Python, C++, CMake, Conan, Docker, GitHub Actions)
7. How to run locally via Docker
8. How to run natively

## Development Notes for Claude Code

Build order:
1. C++ solver first — validate against known analytical limits (OPR=1
   should give near-zero specific thrust above inlet ram contribution;
   TIT equal to ambient temperature should give near-zero SFC)
2. Python subprocess wrapper second — test with mock solver output before
   wiring to the real binary
3. Trade study sweep third — vectorized OPR and Mach grid, results to
   numpy array
4. Plotting fourth — matplotlib contour plots with Symphony operating
   point marker
5. Docker and CI last — wrap everything once working locally

Other notes:
- Keep each module independently testable
- solver_interface.py should work with a mock binary for CI environments
  where the C++ build might not be available
- All physical constants in a single constants.py file — no magic numbers
  anywhere else
- The Python/C++ interface is designed so that swapping the subprocess
  solver for a pybind11 shared library later requires changes only to
  solver_interface.py