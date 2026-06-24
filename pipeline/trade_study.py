"""OPR x Mach trade study sweep and contour plot generation.

Builds a 2D grid of operating points, evaluates the engine cycle solver at
each point, and returns results as numpy arrays ready for plotting.
Plot functions produce specific thrust and
<a href="acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
contour plots over the
<a href="acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
x Mach grid.
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from pipeline import constants
from pipeline.solver_interface import run_solver

# Padding added to the right x-axis limit so markers at the Mach boundary
# are not clipped by the axes frame.
_MACH_AXIS_PAD = 0.05


@dataclass
class TradeStudyResults:
    """Results from a full OPR x Mach trade study sweep.

    All arrays share shape (n_mach, n_opr).

    Attributes:
        mach_grid: Meshgrid of Mach numbers.
        opr_grid: Meshgrid of overall pressure ratios.
        specific_thrust: Net specific thrust in N/(kg/s) at each grid point.
        sfc: Specific fuel consumption in kg/(s*N) at each grid point.
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


def plot_trade_study(
    results: TradeStudyResults,
    output_dir: Path | str = "outputs",
    operating_point: tuple[float, float] | None = (
        constants.SYMPHONY_MACH,
        constants.SYMPHONY_OPR,
    ),
) -> None:
    """Generate and save specific thrust and SFC grid plots.

    Both plots share the same axis layout: Mach number on the x-axis,
    OPR on the y-axis. Each grid cell is rendered as a solid color block
    with no interpolation. The optional operating point is marked with a
    star and labeled.

    Args:
        results: Trade study output from run_trade_study.
        output_dir: Directory to write plot files. Created if absent.
        operating_point: (Mach, OPR) of the reference point to mark on both
            plots. Pass None to omit the marker.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    _plot_specific_thrust(results, out, operating_point)
    _plot_sfc(results, out, operating_point)


def _add_operating_point(
    ax: plt.Axes,
    operating_point: tuple[float, float] | None,
) -> None:
    if operating_point is None:
        return
    mach, opr = operating_point
    ax.plot(mach, opr, marker="*", markersize=14, color="white",
            markeredgecolor="black", markeredgewidth=0.8, zorder=5)
    ax.annotate(
        f"Symphony-like\n(M={mach}, OPR={opr:.0f})",
        xy=(mach, opr),
        xytext=(-6, 0),
        textcoords="offset points",
        fontsize=8,
        color="white",
        ha="right",
        va="center",
    )


def _plot_specific_thrust(
    results: TradeStudyResults,
    out: Path,
    operating_point: tuple[float, float] | None,
    vmin: float | None = None,
    vmax: float | None = None,
    levels: np.ndarray | None = None,
    title_suffix: str = "TIT = 1600 K, Alt = 60,000 ft",
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 6))

    cf = ax.pcolormesh(
        results.mach_grid, results.opr_grid, results.specific_thrust,
        cmap="plasma", shading="nearest", vmin=vmin, vmax=vmax,
    )
    cs = ax.contour(
        results.mach_grid, results.opr_grid, results.specific_thrust,
        levels=levels if levels is not None else 15,
        colors="white", linewidths=0.5, alpha=0.6,
    )
    ax.clabel(cs, fmt="%.0f", fontsize=9)
    fig.colorbar(cf, ax=ax, label="Specific Thrust [N/(kg/s)]")

    _add_operating_point(ax, operating_point)

    ax.set_xlim(results.mach_grid.min(), results.mach_grid.max() + _MACH_AXIS_PAD)
    ax.set_xlabel("Mach Number")
    ax.set_ylabel("Overall Pressure Ratio (OPR)")
    ax.set_title(f"Specific Thrust - OPR x Mach Sweep\n{title_suffix}",
                 fontweight="bold")

    fig.tight_layout()
    if out is not None:
        fig.savefig(out / "specific_thrust.png", dpi=150)
        plt.close(fig)
    return fig


def _plot_sfc(
    results: TradeStudyResults,
    out: Path,
    operating_point: tuple[float, float] | None,
    vmin: float | None = None,
    vmax: float | None = None,
    levels: np.ndarray | None = None,
    title_suffix: str = "TIT = 1600 K, Alt = 60,000 ft",
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 6))

    # Scale SFC to mg/(s*N) for readability on the plot
    sfc_scaled = results.sfc * 1e6

    cf = ax.pcolormesh(
        results.mach_grid, results.opr_grid, sfc_scaled,
        cmap="viridis", shading="nearest", vmin=vmin, vmax=vmax,
    )
    cs = ax.contour(
        results.mach_grid, results.opr_grid, sfc_scaled,
        levels=levels if levels is not None else 15,
        colors="white", linewidths=0.5, alpha=0.6,
    )
    ax.clabel(cs, fmt="%.1f", fontsize=9)
    fig.colorbar(cf, ax=ax, label="SFC [mg/(s*N)]")

    _add_operating_point(ax, operating_point)

    ax.set_xlim(results.mach_grid.min(), results.mach_grid.max() + _MACH_AXIS_PAD)
    ax.set_xlabel("Mach Number")
    ax.set_ylabel("Overall Pressure Ratio (OPR)")
    ax.set_title(f"Specific Fuel Consumption - OPR x Mach Sweep\n{title_suffix}",
                 fontweight="bold")

    fig.tight_layout()
    if out is not None:
        fig.savefig(out / "sfc.png", dpi=150)
        plt.close(fig)
    return fig
