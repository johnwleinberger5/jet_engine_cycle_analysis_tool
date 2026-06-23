# MAINTAINER NOTE — ACRONYM CONVENTION
# Every acronym in this docstring uses the pattern:
#   <a href="acronyms.html#ID"><abbr title="Full Name">ACRONYM</abbr></a>
# When adding or editing content, follow this convention for all acronyms.
# Full reference: pipeline/acronyms.py
"""
# Changelog & Roadmap

---

## v0.1.0 — Current

**Physics solver**

- 1D Brayton cycle (6-station) C++ solver via
  <a href="acronyms.html#CICD"><abbr title="Continuous Integration / Continuous Deployment">CI/CD</abbr></a>-validated subprocess interface
- Normal shock total pressure recovery (Rayleigh Pitot formula)
- <a href="acronyms.html#ISA"><abbr title="International Standard Atmosphere">ISA</abbr></a>
  standard atmosphere (troposphere + stratosphere)
- Isentropic efficiency model for compressor and turbine
  (<a href="acronyms.html#eta_c"><abbr title="Compressor isentropic efficiency">eta_c</abbr></a>,
  <a href="acronyms.html#eta_t"><abbr title="Turbine isentropic efficiency">eta_t</abbr></a>)

**Software infrastructure**

- C++ built with CMake + Conan; Python orchestration via `pyproject.toml`
- Full test suite: 17 C++ unit tests (Catch2/CTest) + 45 Python tests (pytest)
- Docker multi-stage build for reproducible execution
- 5-stage GitHub Actions
  <a href="acronyms.html#CICD"><abbr title="Continuous Integration / Continuous Deployment">CI/CD</abbr></a>
  pipeline (build → test → trade study → Docker → docs)
- Auto-generated documentation deployed to GitHub Pages via pdoc

**Trade study**

-
  <a href="acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
  (10–40) × Mach (0.5–1.7) full-factorial sweep at fixed
  <a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
  = 1600 K, altitude = 60,000 ft
- Specific thrust and
  <a href="acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
  contour plots with Symphony-like operating point marked

---

## Planned

### Nanobind Python/C++ interface

The current subprocess + JSON interface will be replaced by a
[nanobind](https://github.com/wjakob/nanobind) shared library,
making solver calls a direct in-process Python function call with no serialization overhead.
The subprocess path will remain available as a fallback.
This upgrade requires changes only to `pipeline/solver_interface.py` — the rest of the
stack is unaffected. nanobind was chosen over pybind11 for its smaller binary size,
leaner API, and better C++17 alignment.

### LHS sampling + MLP surrogate

Replace the full-factorial
<a href="acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
× Mach grid with a Latin Hypercube Sampling (LHS) design (~10,000 points),
then train a multi-layer perceptron (MLP) surrogate using PyTorch with Optuna
for hyperparameter search (network depth, width, learning rate).
The surrogate generates the contour plots, supplemented by R² score and
training loss vs. epoch curves to demonstrate model accuracy.

### Future fidelity improvements

See [Physics — Model Assumptions & Limitations](physics.html#model-assumptions--limitations)
for a full list of known simplifications and what higher-fidelity would add.

---

## Notes

**Constants single source of truth** — physical and model constants are maintained
separately in `pipeline/constants.py` (Python) and `solver/src/constants.h` (C++).
All values are verified to match. A future improvement would unify them behind a
single `constants.json` or `constants.yaml` read by both runtimes at startup.
"""

# This module exists solely as a documentation page rendered by pdoc.
# It contains no executable code.
_DOCS_ONLY = True
