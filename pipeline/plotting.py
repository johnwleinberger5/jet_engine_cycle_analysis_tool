"""Contour plot generation for trade study results.

Produces specific thrust and SFC contour plots over the OPR × Mach grid,
with an optional reference operating point marker.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from pipeline import constants
from pipeline.trade_study import TradeStudyResults


def plot_trade_study(
    results: TradeStudyResults,
    output_dir: Path | str = "outputs",
    operating_point: tuple[float, float] | None = (
        constants.SYMPHONY_MACH,
        constants.SYMPHONY_OPR,
    ),
) -> None:
    """Generate and save specific thrust and SFC contour plots.

    Both plots share the same axis layout: Mach number on the x-axis,
    OPR on the y-axis, with filled contours and labelled contour lines.
    The optional operating point is marked with a star and labelled.

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
        f"  Symphony-like\n  (M={mach}, OPR={opr:.0f})",
        xy=(mach, opr),
        fontsize=8,
        color="white",
        va="center",
    )


def _plot_specific_thrust(
    results: TradeStudyResults,
    out: Path,
    operating_point: tuple[float, float] | None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    cf = ax.contourf(
        results.mach_grid, results.opr_grid, results.specific_thrust,
        levels=20, cmap="plasma"
    )
    cs = ax.contour(
        results.mach_grid, results.opr_grid, results.specific_thrust,
        levels=10, colors="white", linewidths=0.5, alpha=0.6
    )
    ax.clabel(cs, fmt="%.0f", fontsize=7)
    fig.colorbar(cf, ax=ax, label="Specific Thrust [N/(kg/s)]")

    _add_operating_point(ax, operating_point)

    ax.set_xlabel("Mach Number")
    ax.set_ylabel("Overall Pressure Ratio (OPR)")
    ax.set_title("Specific Thrust — OPR × Mach Sweep\n"
                 "TIT = 1600 K, Alt = 60,000 ft")

    fig.tight_layout()
    fig.savefig(out / "specific_thrust.png", dpi=150)
    plt.close(fig)


def _plot_sfc(
    results: TradeStudyResults,
    out: Path,
    operating_point: tuple[float, float] | None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    # Scale SFC to mg/(s·N) for readability on the plot
    sfc_scaled = results.sfc * 1e6

    cf = ax.contourf(
        results.mach_grid, results.opr_grid, sfc_scaled,
        levels=20, cmap="viridis"
    )
    cs = ax.contour(
        results.mach_grid, results.opr_grid, sfc_scaled,
        levels=10, colors="white", linewidths=0.5, alpha=0.6
    )
    ax.clabel(cs, fmt="%.1f", fontsize=7)
    fig.colorbar(cf, ax=ax, label="SFC [mg/(s·N)]")

    _add_operating_point(ax, operating_point)

    ax.set_xlabel("Mach Number")
    ax.set_ylabel("Overall Pressure Ratio (OPR)")
    ax.set_title("Specific Fuel Consumption — OPR × Mach Sweep\n"
                 "TIT = 1600 K, Alt = 60,000 ft")

    fig.tight_layout()
    fig.savefig(out / "sfc.png", dpi=150)
    plt.close(fig)
