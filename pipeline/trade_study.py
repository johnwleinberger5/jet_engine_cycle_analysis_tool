"""OPR × Mach trade study sweep.

Builds a 2D grid of operating points, evaluates the engine cycle solver at
each point, and returns results as numpy arrays ready for plotting.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from pipeline import constants
from pipeline.solver_interface import run_solver


@dataclass
class TradeStudyResults:
    """Results from a full OPR × Mach trade study sweep.

    All arrays share shape (n_mach, n_opr).

    Attributes:
        mach_grid: Meshgrid of Mach numbers.
        opr_grid: Meshgrid of overall pressure ratios.
        specific_thrust: Net specific thrust in N/(kg/s) at each grid point.
        sfc: Specific fuel consumption in kg/(s·N) at each grid point.
    """
    mach_grid: np.ndarray
    opr_grid: np.ndarray
    specific_thrust: np.ndarray
    sfc: np.ndarray


def run_trade_study(
    mach_range: tuple[float, float] = (constants.MACH_MIN, constants.MACH_MAX),
    opr_range: tuple[float, float] = (constants.OPR_MIN, constants.OPR_MAX),
    n_mach: int = constants.N_MACH,
    n_opr: int = constants.N_OPR,
    tit_k: float = constants.TIT_K,
    altitude_ft: float = constants.ALT_FT,
    solver_path: Path | None = None,
) -> TradeStudyResults:
    """Sweep OPR and Mach number and return performance over the full grid.

    Args:
        mach_range: (min, max) Mach number bounds, inclusive.
        opr_range: (min, max) overall pressure ratio bounds, inclusive.
        n_mach: Number of Mach points in the sweep.
        n_opr: Number of OPR points in the sweep.
        tit_k: Turbine inlet temperature in Kelvin, fixed across sweep.
        altitude_ft: Cruise altitude in feet, fixed across sweep.
        solver_path: Path to the solver binary, passed through to run_solver.
            If None, uses the default path in solver_interface.

    Returns:
        TradeStudyResults containing meshgrid arrays and corresponding
        specific thrust and SFC arrays, each of shape (n_mach, n_opr).
    """
    mach_vec = np.linspace(mach_range[0], mach_range[1], n_mach)
    opr_vec  = np.linspace(opr_range[0],  opr_range[1],  n_opr)

    mach_grid, opr_grid = np.meshgrid(mach_vec, opr_vec, indexing="ij")

    specific_thrust = np.empty((n_mach, n_opr))
    sfc             = np.empty((n_mach, n_opr))

    for i, mach in enumerate(mach_vec):
        for j, opr in enumerate(opr_vec):
            result = run_solver(
                mach=mach,
                opr=opr,
                tit_k=tit_k,
                altitude_ft=altitude_ft,
                solver_path=solver_path,
            )
            specific_thrust[i, j] = result.specific_thrust_n_per_kgs
            sfc[i, j]             = result.sfc_kg_per_s_per_n

    return TradeStudyResults(
        mach_grid=mach_grid,
        opr_grid=opr_grid,
        specific_thrust=specific_thrust,
        sfc=sfc,
    )
