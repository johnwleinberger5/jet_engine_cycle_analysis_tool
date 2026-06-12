"""Entry point for the OPR × Mach trade study.

Runs the full sweep and writes specific thrust and SFC contour plots to
the outputs/ directory.
"""

from pipeline.trade_study import run_trade_study
from pipeline.plotting import plot_trade_study


def main() -> None:
    results = run_trade_study()
    plot_trade_study(results)
    print("Trade study complete. Plots written to outputs/")


if __name__ == "__main__":
    main()
