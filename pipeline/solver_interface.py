"""Interface between Python and the C++ engine cycle solver.

The solver binary is invoked as a subprocess. Inputs are serialized to JSON
and written to the process stdin; results are read from stdout and
deserialized. This module is the sole boundary between Python and C++ —
swapping the subprocess for a pybind11 module requires changes only here.
"""

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from pipeline import constants


def _find_solver_binary() -> Path:
    """Locate the solver binary, accounting for platform build layout.

    Resolution order:
    1. ENGINE_SOLVER_PATH environment variable (explicit override; set in Docker)
    2. __file__-relative paths (works for local editable installs)
       - Linux/Mac (single-config): solver/build/solver
       - Windows MSVC (multi-config): solver/build/Release/solver.exe
    """
    env_path = os.environ.get("ENGINE_SOLVER_PATH")
    if env_path:
        return Path(env_path)

    base = Path(__file__).parent.parent / "solver" / "build"
    candidates = [
        base / "solver",
        base / "solver.exe",
        base / "Release" / "solver.exe",
        base / "Release" / "solver",
    ]
    for path in candidates:
        if path.exists():
            return path
    return base / "solver"  # fallback — will raise FileNotFoundError at call time


_DEFAULT_SOLVER_PATH = _find_solver_binary()


@dataclass
class SolverResult:
    """Output from a single engine cycle solver evaluation.

    Attributes:
        specific_thrust_n_per_kgs: Net specific thrust in N/(kg/s of airflow).
        sfc_kg_per_s_per_n: Specific fuel consumption in kg/(s·N).
        t0_stations_k: Total temperature at each of the 6 stations in Kelvin.
            Order: [freestream, inlet exit, compressor exit, combustor exit,
            turbine exit, nozzle exit].
        p0_stations_pa: Total pressure at each of the 6 stations in Pascals.
            Same station order as t0_stations_k.
    """
    specific_thrust_n_per_kgs: float
    sfc_kg_per_s_per_n: float
    t0_stations_k: list[float]
    p0_stations_pa: list[float]


def run_solver(
    mach: float,
    opr: float,
    tit_k: float = constants.TIT_K,
    altitude_ft: float = constants.ALT_FT,
    solver_path: Path | None = None,
) -> SolverResult:
    """Run the C++ engine cycle solver for a single operating point.

    Serializes inputs to JSON, invokes the solver binary via subprocess,
    and deserializes the result. This is the sole interface boundary between
    Python and C++; swapping the subprocess for a pybind11 module requires
    changes only here.

    Args:
        mach: Freestream Mach number. Must be > 0.
        opr: Overall pressure ratio. Must be > 1.
        tit_k: Turbine inlet temperature in Kelvin. Defaults to 1600 K.
        altitude_ft: Cruise altitude in feet. Defaults to 60,000 ft.
        solver_path: Path to the solver binary. If None, resolves to
            ``solver/build/solver`` relative to the repo root.

    Returns:
        SolverResult with specific thrust, SFC, and per-station total
        temperature and pressure arrays.

    Raises:
        FileNotFoundError: If the solver binary cannot be found.
        RuntimeError: If the solver exits with a non-zero return code.
        ValueError: If the solver output cannot be parsed.
    """
    path = Path(solver_path) if solver_path is not None else _DEFAULT_SOLVER_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Solver binary not found at {path}. "
            "Build the C++ solver with: cd solver && cmake --build build"
        )

    payload = json.dumps({
        "mach": mach,
        "opr": opr,
        "tit_k": tit_k,
        "altitude_ft": altitude_ft,
    })

    proc = subprocess.run(
        [str(path)],
        input=payload,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Solver exited with code {proc.returncode}. stderr:\n{proc.stderr}"
        )

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Could not parse solver output as JSON: {e}\nOutput was:\n{proc.stdout}"
        )

    return SolverResult(
        specific_thrust_n_per_kgs=data["specific_thrust_n_per_kgs"],
        sfc_kg_per_s_per_n=data["sfc_kg_per_s_per_n"],
        t0_stations_k=data["t0_stations_k"],
        p0_stations_pa=data["p0_stations_pa"],
    )
